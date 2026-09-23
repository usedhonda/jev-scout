import json
import base64
import io
import os
import pathlib
import stat
import tempfile
import subprocess
import shutil
import unittest
from unittest import mock

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "skills" / "jev-scout" / "scripts"))
import jev_scout


def docs(max_requests=2, max_input_bytes=10000, max_retries=1):
    experiment = {"model": "jev-1", "revision": "r1", "cases": [
        {"id": "a", "state": {"secret": "do-not-preview"}, "questions": {"q": {"type": "choice", "instructions": "pick", "criteria": {"yes": "matches", "no": "does not match"}}}, "expected": {"q": "yes"}}
    ]}
    policy = {"approved": True, "data_scope": "fixture", "max_requests": max_requests,
              "max_input_bytes": max_input_bytes, "max_seconds": 5, "max_retries": max_retries}
    return experiment, policy


class RunnerTests(unittest.TestCase):
    def test_preview_has_sizes_and_no_state_or_key(self):
        exp, policy = docs()
        out = jev_scout._preview(exp, policy)
        self.assertIn("request_bytes", out)
        self.assertNotIn("secret", json.dumps(out))
        with mock.patch.object(jev_scout, "_default_transport") as transport:
            self.assertEqual(jev_scout.main(["preview", "--experiment", "x", "--policy", "y"]), 2)
            transport.assert_not_called()

    def test_key_file_precedes_environment_and_rejects_injection(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "key"
            p.write_bytes(b"TYPESAFE_API_KEY=file-key\n")
            with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-key"}):
                self.assertEqual(jev_scout._key(str(p)), "file-key")
            p.write_bytes(b"TYPESAFE_API_KEY=x\nEVIL=y")
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._key(str(p))

    def test_retry_429_and_sanitize_answers(self):
        exp, policy = docs(max_retries=1)
        calls = []
        def transport(body, key, timeout):
            calls.append(timeout)
            if len(calls) == 1:
                return 429, b"retry body"
            return 200, b'{"model":"jev-1","answers":{"q":{"type":"choice","choice":"yes","confidence":0.95,"raw":"secret"}},"usage":{"input_tokens":1,"output_tokens":1}}'
        with mock.patch.object(jev_scout.time, "sleep"):
            out = jev_scout._run(exp, policy, "key", transport)
        self.assertEqual(out["results"][0]["status"], "ok")
        self.assertEqual(out["results"][0]["correctness"], {"q": True})
        self.assertEqual(out["results"][0]["attempts"], 2)
        self.assertNotIn("secret", json.dumps(out))

    def test_401_stops_without_retry(self):
        exp, policy = docs(max_retries=1)
        exp["cases"].append(dict(exp["cases"][0], id="b"))
        calls = []
        def transport(body, key, timeout):
            calls.append(1)
            return 401, b"secret response"
        out = jev_scout._run(exp, policy, "key", transport)
        self.assertEqual(len(calls), 1)
        self.assertEqual(out["results"][0]["status"], "unauthorized")
        self.assertEqual(out["results"][0]["http_status"], 401)

    def test_403_access_denied_stops_and_classifies_bounded_edge_body(self):
        exp, policy = docs(max_retries=3)
        exp["cases"].append(dict(exp["cases"][0], id="b"))
        calls = []

        def transport(body, key, timeout):
            calls.append(1)
            return 403, b" \nerror code: 1010\r\t"

        out = jev_scout._run(exp, policy, "key", transport)
        self.assertEqual(len(calls), 1)
        self.assertFalse(out["complete"])
        self.assertEqual(out["cases_expected"], 2)
        self.assertEqual(out["cases_completed"], 0)
        self.assertEqual(out["results"][0]["status"], "access_denied")
        self.assertEqual(out["results"][0]["diagnostic_code"], "edge_1010")

    def test_403_poisoned_body_is_not_exposed_or_misclassified(self):
        exp, policy = docs()
        for poisoned in (b"error code: 1010 attacker-secret", b"error code: 1010" + b" " * 4090 + b"attacker-secret"):
            out = jev_scout._run(exp, policy, "key", lambda *_: (403, poisoned))
            self.assertEqual(out["results"][0]["status"], "access_denied")
            self.assertNotIn("diagnostic_code", out["results"][0])
            self.assertNotIn("attacker-secret", json.dumps(out))

    def test_cli_incomplete_summary_is_terminal_and_safe(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            exp, policy = docs()
            (root / "exp.json").write_text(json.dumps(exp))
            (root / "policy.json").write_text(json.dumps(policy))
            output = root / "result.json"
            incomplete = {"model": "jev-1", "results": [{"status": "access_denied"}],
                          "requests": 1, "input_bytes": 10, "cases_expected": 1,
                          "cases_completed": 0, "complete": False}
            stdout = io.StringIO()
            with mock.patch.object(jev_scout, "_run", return_value=incomplete), \
                 mock.patch.object(jev_scout, "_key", return_value="key"), \
                 mock.patch("sys.stdout", stdout):
                self.assertEqual(jev_scout.main(["run", "--experiment", str(root / "exp.json"),
                                                 "--policy", str(root / "policy.json"), "--output", str(output)]), 1)
            summary = json.loads(stdout.getvalue())
            self.assertEqual(summary, {"status": "incomplete", "cases_expected": 1,
                                       "cases_completed": 0, "requests": 1,
                                       "failure_statuses": ["access_denied"], "output": str(output)})

    def test_input_cap_and_output_protection(self):
        exp, policy = docs(max_input_bytes=1)
        with self.assertRaises(jev_scout.RunnerError):
            jev_scout._run(exp, policy, "key", lambda *_: (200, b'{}'))
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "result.json"
            jev_scout._write_result(str(path), {"ok": True})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._write_result(str(path), {"again": True})

    def test_actual_attempt_caps_and_invalid_response(self):
        exp, policy = docs(max_requests=1, max_retries=3)
        transport = mock.Mock(return_value=(429, b"private error"))
        with mock.patch.object(jev_scout.time, "sleep"):
            out = jev_scout._run(exp, policy, "key", transport)
        self.assertEqual(transport.call_count, 1)
        self.assertEqual(out["requests"], 1)
        self.assertFalse(out["complete"])
        for response in (b'{}', b'{"model":"jev-1","answers":{"q":{"type":"choice","choice":"private-echo","confidence":1}},"usage":{"input_tokens":1,"output_tokens":1}}'):
            out = jev_scout._run(exp, policy, "key", lambda *_: (200, response))
            self.assertEqual(out["results"][0]["status"], "invalid_response")
            self.assertNotIn("private-echo", json.dumps(out))

    def test_unapproved_preview_and_nonfinite_limit(self):
        exp, policy = docs()
        policy["approved"] = False
        self.assertFalse(jev_scout._preview(exp, policy)["approved"])
        with self.assertRaises(jev_scout.RunnerError):
            jev_scout._run(exp, policy, "key")
        policy["approved"] = True
        policy["max_seconds"] = float("nan")
        with self.assertRaises(jev_scout.RunnerError):
            jev_scout._preview(exp, policy)

    def test_no_redirect_and_invalid_binding_no_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "local.json").write_text('{"key_file":"relative.env"}')
            with mock.patch.object(jev_scout, "__file__", str(root / "scripts/runner.py")), mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-key"}):
                with self.assertRaises(jev_scout.RunnerError):
                    jev_scout._key(None)

    def test_node_transport_helper_uses_fixed_request_and_bounds_error(self):
        with tempfile.TemporaryDirectory() as td:
            helper = pathlib.Path(td) / "path with spaces" / "jev_transport.mjs"
            helper.parent.mkdir()
            shutil.copyfile(pathlib.Path(jev_scout.__file__).with_name("jev_transport.mjs"), helper)
            self._run_node_transport_assertions(helper)

    def _run_node_transport_assertions(self, helper):
        script = """
import { transport } from %s;
const input = JSON.parse(await new Promise((resolve) => {
  let s = ''; process.stdin.on('data', (c) => s += c);
  process.stdin.on('end', () => resolve(s));
}));
const out = await transport(input, async (url, options) => {
  if (url !== 'https://api.typesafe.ai/v1/systemone' || options.method !== 'POST' ||
      options.redirect !== 'error' || options.headers.Authorization !== 'Bearer test-key' ||
      options.headers['Content-Type'] !== 'application/json' ||
      Buffer.from(options.body).toString() !== 'body' || !(options.signal instanceof AbortSignal)) process.exit(3);
  return new Response('error code: 1010' + ' '.repeat(4090) + 'secret', { status: 403 });
});
process.stdout.write(JSON.stringify(out));
""" % json.dumps(str(helper))
        payload = json.dumps({"key": "test-key", "body": base64.b64encode(b"body").decode(), "timeout_ms": 1000}).encode()
        completed = subprocess.run(["node", "--input-type=module", "-e", script], input=payload,
                                   capture_output=True, check=True)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], 403)
        error_body = base64.b64decode(result["body"])
        self.assertEqual(len(error_body), 4097)
        self.assertNotIn(b"attacker-secret", error_body)

    def test_default_transport_rejects_missing_or_old_node(self):
        with mock.patch.object(jev_scout.shutil, "which", return_value=None):
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._default_transport(b"{}", "key", 1)
        with mock.patch.object(jev_scout.shutil, "which", return_value="node"), \
             mock.patch.object(jev_scout.subprocess, "run", return_value=mock.Mock(stdout="v21.9.0")):
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._default_transport(b"{}", "key", 1)

    def test_default_transport_rejects_failed_or_invalid_child(self):
        version = mock.Mock(stdout="v24.2.0")
        failed = mock.Mock(returncode=1, stdout=b"", stderr=b"secret")
        with mock.patch.object(jev_scout.shutil, "which", return_value="node"), \
             mock.patch.object(jev_scout.subprocess, "run", side_effect=[version, failed]):
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._default_transport(b"{}", "key", 1)
        invalid = mock.Mock(returncode=0, stdout=b"[]", stderr=b"")
        with mock.patch.object(jev_scout.shutil, "which", return_value="node"), \
             mock.patch.object(jev_scout.subprocess, "run", side_effect=[version, invalid]):
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._default_transport(b"{}", "key", 1)
    def test_output_preflight_prevents_api_call(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            exp, policy = docs()
            (root / "exp.json").write_text(json.dumps(exp))
            (root / "policy.json").write_text(json.dumps(policy))
            (root / "result.json").write_text("existing")
            with mock.patch.object(jev_scout, "_run") as run:
                self.assertEqual(jev_scout.main(["run", "--experiment", str(root / "exp.json"), "--policy", str(root / "policy.json"), "--output", str(root / "result.json")]), 2)
                run.assert_not_called()

    def test_typed_numeric_answers_and_missing_id(self):
        questions = {"n": {"type": "noul"}, "s": {"type": "score", "criteria": ["low", "high"]}}
        parsed = {"answers": {"n": {"type": "noul", "noul": .8}, "s": {"type": "score", "score": .7, "confidence": .6}}}
        self.assertEqual(jev_scout._answers(parsed, questions)["s"]["score"], .7)
        parsed["answers"].pop("n")
        with self.assertRaises(jev_scout.RunnerError):
            jev_scout._answers(parsed, questions)

    def test_optional_probabilities_are_validated_and_preserved(self):
        questions = {
            "c": {"type": "choice", "criteria": {"yes": "", "no": ""}},
            "s": {"type": "score", "criteria": ["low", "mid", "high"]},
        }
        parsed = {"answers": {
            "c": {"type": "choice", "choice": "yes", "confidence": .8,
                  "probabilities": {"yes": .8, "no": .2}},
            "s": {"type": "score", "score": 1, "confidence": .7,
                  "probabilities": {"0": 0.1, "1": 0.7, "2": 0.2}},
        }}
        clean = jev_scout._answers(parsed, questions)
        self.assertEqual(clean["c"]["probabilities"], parsed["answers"]["c"]["probabilities"])
        self.assertEqual(clean["s"]["probabilities"], parsed["answers"]["s"]["probabilities"])
        self.assertNotIn("probabilities", jev_scout._answers({"answers": {
            "c": {"type": "choice", "choice": "yes", "confidence": .8},
            "s": {"type": "score", "score": 1, "confidence": .7},
        }}, questions)["c"])
        invalid = [
            {"yes": .8},
            {"yes": .8, "no": float("nan")},
            {"yes": True, "no": 0.0},
            {"yes": .5, "no": .5 + 2e-4},
        ]
        for probabilities in invalid:
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._answers({"answers": {
                    "c": {"type": "choice", "choice": "yes", "confidence": .8, "probabilities": probabilities},
                    "s": {"type": "score", "score": 1, "confidence": .7},
                }}, questions)

    def test_target_revision_is_optional_validated_and_only_result_metadata(self):
        exp, policy = docs()
        revision = {"base_sha": "a" * 40, "head_sha": "b" * 40}
        exp["target_revision"] = revision
        seen = []
        def transport(body, key, timeout):
            seen.append(json.loads(body))
            return 200, b'{"model":"jev-1","answers":{"q":{"type":"choice","choice":"yes","confidence":1}},"usage":{"input_tokens":1,"output_tokens":1}}'
        out = jev_scout._run(exp, policy, "key", transport)
        self.assertEqual(out["target_revision"], revision)
        self.assertNotIn("target_revision", seen[0])
        self.assertEqual(exp["revision"], "r1")
        for bad in (
            {"base_sha": "a" * 40},
            {"head_sha": "b" * 40, "dirty": True},
            {"head_sha": "b" * 40, "dirty": True, "diff_sha256": "x" * 64},
            {"head_sha": "b" * 40, "private_path": "/tmp/x"},
        ):
            exp["target_revision"] = bad
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._run(exp, policy, "key", transport)

    def test_retry_bytes_and_cross_directory_output(self):
        exp, policy = docs(max_requests=3, max_retries=2)
        policy["max_input_bytes"] = jev_scout._preview(exp, policy)["total_request_bytes"]
        transport = mock.Mock(return_value=(529, b"not recorded"))
        with mock.patch.object(jev_scout.time, "sleep"):
            out = jev_scout._run(exp, policy, "key", transport)
        self.assertEqual(transport.call_count, 1)
        self.assertEqual(out["input_bytes"], policy["max_input_bytes"])
        self.assertEqual(out["requests"], 1)
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td).resolve()
            import subprocess
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / ".gitignore").write_text("private/\n")
            self.assertEqual(jev_scout._check_output_path(str(root / "private/result.json")), root / "private/result.json")
            with self.assertRaises(jev_scout.RunnerError):
                jev_scout._check_output_path(str(root / "public/result.json"))


if __name__ == "__main__":
    unittest.main()
