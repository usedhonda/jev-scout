#!/usr/bin/env python3
"""Small, bounded, stdlib-only runner for Jev Scout experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import math
import time
import base64
from typing import Any, Callable

API_URL = "https://api.typesafe.ai/v1/systemone"
MAX_BACKOFF = 2.0
_EDGE_1010_BODY = re.compile(rb"[\x09\x0a\x0b\x0c\x0d\x20]*error code: 1010[\x09\x0a\x0b\x0c\x0d\x20]*\Z")


class RunnerError(Exception):
    pass


def _target_revision(experiment: dict[str, Any]) -> dict[str, Any] | None:
    """Validate and copy optional provenance metadata without exposing it to the API."""
    if "target_revision" not in experiment:
        return None
    value = experiment["target_revision"]
    if not isinstance(value, dict):
        raise RunnerError("experiment target_revision must be an object")
    allowed = {"base_sha", "head_sha", "diff_sha256", "dirty"}
    if set(value) - allowed:
        raise RunnerError("experiment target_revision has unknown fields")
    clean: dict[str, Any] = {}
    for name in ("base_sha", "head_sha"):
        if name in value:
            sha = value[name]
            if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdefABCDEF" for c in sha):
                raise RunnerError(f"experiment target_revision {name} must be a 40-character hex SHA")
            clean[name] = sha
    if "diff_sha256" in value:
        digest = value["diff_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            raise RunnerError("experiment target_revision diff_sha256 must be a 64-character hex digest")
        clean["diff_sha256"] = digest
    if "dirty" in value:
        if not isinstance(value["dirty"], bool):
            raise RunnerError("experiment target_revision dirty must be boolean")
        clean["dirty"] = value["dirty"]
    if "base_sha" in clean and "head_sha" not in clean:
        raise RunnerError("experiment target_revision base_sha requires head_sha")
    if clean.get("dirty") is True and not {"head_sha", "diff_sha256"} <= clean.keys():
        raise RunnerError("dirty target_revision requires head_sha and diff_sha256")
    if "diff_sha256" in clean and clean.get("dirty") is not True:
        raise RunnerError("target_revision diff_sha256 requires dirty=true")
    return clean


def _read_json(path: str) -> tuple[dict[str, Any], bytes]:
    p = pathlib.Path(path)
    try:
        raw = p.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunnerError(f"cannot read JSON: {p}") from exc
    if not isinstance(value, dict):
        raise RunnerError(f"JSON root must be an object: {p}")
    return value, raw


def _positive(value: Any, name: str, integer: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise RunnerError(f"policy {name} must be positive")
    if integer and not isinstance(value, int):
        raise RunnerError(f"policy {name} must be an integer")


def _validate(experiment: dict[str, Any], policy: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(experiment.get("model"), str) or not experiment["model"]:
        raise RunnerError("experiment model is required")
    _target_revision(experiment)
    cases = experiment.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RunnerError("experiment cases must be a non-empty list")
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"] or case["id"] in ids:
            raise RunnerError("each case requires an id")
        ids.add(case["id"])
        if not isinstance(case.get("state"), (str, dict, list)) or not isinstance(case.get("questions"), dict) or not case["questions"]:
            raise RunnerError("each case requires state and questions")
        for qid, question in case["questions"].items():
            if not qid or not isinstance(question, dict) or question.get("type") not in {"choice", "noul", "score"} or not question.get("instructions"):
                raise RunnerError("invalid typed question")
            criteria = question.get("criteria")
            if question["type"] == "choice" and (not isinstance(criteria, dict) or not 1 <= len(criteria) <= 255):
                raise RunnerError("Choice requires a nonempty criteria map")
            if question["type"] == "score" and (not isinstance(criteria, list) or not 2 <= len(criteria) <= 10):
                raise RunnerError("Score requires 2 to 10 levels")
        expected = case.get("expected", {})
        if not isinstance(expected, dict) or any(qid not in case["questions"] for qid in expected):
            raise RunnerError("case expected must be an object")
        for qid, value in expected.items():
            q = case["questions"][qid]
            if q["type"] == "choice" and (not isinstance(value, str) or value not in q["criteria"]):
                raise RunnerError("expected Choice must be a candidate")
            if q["type"] == "noul" and (not isinstance(value, bool) or not _number(case.get("thresholds", {}).get(qid), 0, 1)):
                raise RunnerError("expected Noul needs boolean label and explicit threshold")
            if q["type"] == "score" and not _number(value, 0, len(q["criteria"]) - 1):
                raise RunnerError("expected Score must be on the defined scale")
    if not isinstance(policy.get("approved"), bool) or not policy["approved"]:
        raise RunnerError("policy approved must be true")
    if not isinstance(policy.get("data_scope"), str) or not policy["data_scope"]:
        raise RunnerError("policy data_scope is required")
    _positive(policy.get("max_requests"), "max_requests", True)
    _positive(policy.get("max_input_bytes"), "max_input_bytes", True)
    _positive(policy.get("max_seconds"), "max_seconds")
    retries = policy.get("max_retries")
    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise RunnerError("policy max_retries must be a nonnegative integer")
    return cases


def _key_from_file(path: str) -> str:
    try:
        raw = pathlib.Path(path).read_bytes()
    except OSError as exc:
        raise RunnerError("cannot read key file") from exc
    # Deliberately accept only one exact assignment; never evaluate shell syntax.
    if raw.endswith(b"\n"):
        raw = raw[:-1]
    if b"\n" in raw or b"\r" in raw or not raw.startswith(b"TYPESAFE_API_KEY="):
        raise RunnerError("key file must contain one TYPESAFE_API_KEY= assignment")
    try:
        value = raw[len(b"TYPESAFE_API_KEY="):].decode("ascii", "strict")
    except UnicodeError:
        raise RunnerError("invalid API key encoding") from None
    return _validate_key(value)


def _validate_key(value: str) -> str:
    if not value or any(ord(c) <= 32 or ord(c) >= 127 for c in value) or any(c in value for c in "'\";$`\\"):
        raise RunnerError("invalid API key value")
    return value


def _key(path: str | None) -> str:
    if path:
        return _key_from_file(path)
    binding = pathlib.Path(__file__).resolve().parent.parent / "local.json"
    if binding.exists():
        try:
            configured = json.loads(binding.read_text(encoding="utf-8")).get("key_file")
        except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
            raise RunnerError("invalid local key binding") from None
        if not isinstance(configured, str) or not pathlib.Path(configured).is_absolute():
            raise RunnerError("local key binding requires an absolute key_file")
        return _key_from_file(configured)
    value = os.environ.get("TYPESAFE_API_KEY")
    if not value or any(c.isspace() for c in value):
        raise RunnerError("TYPESAFE_API_KEY is not set")
    return _validate_key(value)


def _key_configured(path: str | None = None) -> bool:
    if path:
        return pathlib.Path(path).is_file()
    binding = pathlib.Path(__file__).resolve().parent.parent / "local.json"
    if binding.exists():
        try:
            value = json.loads(binding.read_text(encoding="utf-8")).get("key_file")
            if isinstance(value, str) and value:
                return pathlib.Path(value if os.path.isabs(value) else binding.parent / value).is_file()
        except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
            return False
        return False
    return bool(os.environ.get("TYPESAFE_API_KEY"))


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _preview(experiment: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    preview_policy = dict(policy)
    preview_policy["approved"] = True
    cases = _validate(experiment, preview_policy)
    sizes = [len(_json_bytes({"model": experiment["model"], "state": c["state"], "questions": c["questions"]})) for c in cases]
    return {"model": experiment["model"], "case_count": len(cases), "request_bytes": sizes,
            "total_request_bytes": sum(sizes), "max_input_bytes": policy["max_input_bytes"],
            "within_limits": len(cases) <= policy["max_requests"] and sum(sizes) <= policy["max_input_bytes"],
            "approved": policy["approved"]}


_TRANSPORT = pathlib.Path(__file__).resolve().with_name("jev_transport.mjs")
_MIN_NODE_VERSION = 22


def _default_transport(body: bytes, key: str, timeout: float) -> tuple[int, bytes]:
    node = shutil.which("node")
    if not node:
        raise RunnerError("Node.js >= 22 is required for API transport")
    try:
        child_env = os.environ.copy()
        child_env.pop("NODE_OPTIONS", None)
        version = subprocess.run([node, "--version"], capture_output=True, text=True,
                                 check=True, timeout=min(5.0, max(0.1, timeout)), env=child_env)
        match = re.fullmatch(r"v(\d+)(?:\.\d+){0,2}\s*", version.stdout)
        if not match or int(match.group(1)) < _MIN_NODE_VERSION:
            raise RunnerError("Node.js >= 22 is required for API transport")
        payload = _json_bytes({"key": key, "body": base64.b64encode(body).decode("ascii"),
                               "timeout_ms": max(1, int(timeout * 1000))})
        completed = subprocess.run([node, str(_TRANSPORT)], input=payload, capture_output=True,
                                   timeout=max(0.1, timeout), check=False, env=child_env)
    except RunnerError:
        raise
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        raise RunnerError("Node.js API transport failed") from exc
    try:
        if completed.returncode != 0:
            raise ValueError("transport child failed")
        result = json.loads(completed.stdout.decode("utf-8"))
        if not isinstance(result, dict):
            raise ValueError("invalid transport response")
        status = result.get("status")
        encoded = result.get("body")
        if (not isinstance(status, int) or not 100 <= status <= 599 or
                not isinstance(encoded, str)):
            raise ValueError("invalid transport response")
        response = base64.b64decode(encoded, validate=True)
        max_bytes = 1024 * 1024 if 200 <= status < 300 else 4097
        if len(response) > max_bytes:
            raise ValueError("transport response exceeded bound")
        return status, response
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise RunnerError("Node.js API transport returned invalid output") from exc


def _number(value: Any, low: float, high: float) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and low <= value <= high


def _answers(parsed: Any, questions: dict) -> dict:
    raw = parsed.get("answers") if isinstance(parsed, dict) else None
    if not isinstance(raw, dict) or set(raw) != set(questions):
        raise RunnerError("answer IDs do not match")
    clean = {}
    for qid, q in questions.items():
        a = raw[qid]
        kind = q["type"]
        if not isinstance(a, dict) or a.get("type") != kind:
            raise RunnerError("answer type does not match")
        value = a.get(kind)
        if kind == "choice":
            if not isinstance(value, str) or value not in q["criteria"]:
                raise RunnerError("answer outside candidates")
        elif not _number(value, 0, 1 if kind == "noul" else len(q["criteria"]) - 1):
            raise RunnerError("answer outside numeric range")
        clean[qid] = {"type": kind, kind: value}
        if kind != "noul":
            if not _number(a.get("confidence"), 0, 1):
                raise RunnerError("invalid confidence")
            clean[qid]["confidence"] = a["confidence"]
            if "probabilities" in a:
                probabilities = a["probabilities"]
                if not isinstance(probabilities, dict):
                    raise RunnerError("invalid probabilities")
                if kind == "choice":
                    expected_keys = set(q["criteria"])
                else:
                    expected_keys = {str(index) for index in range(len(q["criteria"]))}
                if set(probabilities) != expected_keys:
                    raise RunnerError("probability keys do not match candidates")
                if any(not _number(probability, 0, 1) for probability in probabilities.values()):
                    raise RunnerError("invalid probabilities")
                if abs(sum(probabilities.values()) - 1.0) > 1e-4:
                    raise RunnerError("probabilities must sum to one")
                clean[qid]["probabilities"] = dict(probabilities)
    return clean


def _run(experiment: dict[str, Any], policy: dict[str, Any], key: str,
         transport: Callable[[bytes, str, float], tuple[int, bytes]] = _default_transport) -> dict[str, Any]:
    cases = _validate(experiment, policy)
    target_revision = _target_revision(experiment)
    deadline = time.monotonic() + float(policy["max_seconds"])
    total = 0
    request_count = 0
    results = []
    for case in cases:
        body_obj = {"model": experiment["model"], "state": case["state"], "questions": case["questions"]}
        body = _json_bytes(body_obj)
        if len(body) > policy["max_input_bytes"]:
            raise RunnerError("max_input_bytes exceeded")
        started = time.monotonic()
        status = "error"
        answers: dict[str, Any] = {}
        response_model = None
        usage: dict[str, Any] = {}
        attempts = 0
        http_status = None
        for attempt in range(policy["max_retries"] + 1):
            if request_count >= policy["max_requests"]:
                status = "request_cap"
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                status = "deadline"
                break
            if total + len(body) > policy["max_input_bytes"]:
                status = "input_cap"
                break
            attempts += 1
            request_count += 1
            total += len(body)
            try:
                code, response = transport(body, key, remaining)
            except Exception:
                code, response = 0, b""
            http_status = code if isinstance(code, int) and 100 <= code <= 599 else None
            if time.monotonic() > deadline:
                status = "deadline"
                break
            if code == 401:
                status = "unauthorized"
                break
            if code == 403:
                status = "access_denied"
                break
            if code in (429, 529) and attempt < policy["max_retries"]:
                delay = min(MAX_BACKOFF, 0.1 * (2 ** attempt), max(0.0, deadline - time.monotonic()))
                if delay:
                    time.sleep(delay)
                continue
            if 200 <= code < 300:
                try:
                    parsed = json.loads(response.decode("utf-8"))
                    answers = _answers(parsed, case["questions"])
                    model = parsed.get("model")
                    if not isinstance(model, str) or not model.startswith("jev-") or len(model) > 100 or not all(c.isalnum() or c in "-._" for c in model):
                        raise RunnerError("invalid response model")
                    raw_usage = parsed.get("usage")
                    if not isinstance(raw_usage, dict) or any(not isinstance(raw_usage.get(k), int) or isinstance(raw_usage.get(k), bool) or raw_usage[k] < 0 for k in ("input_tokens", "output_tokens")):
                        raise RunnerError("invalid usage")
                    response_model = model
                    usage = {k: raw_usage[k] for k in ("input_tokens", "output_tokens")}
                    status = "ok"
                except (UnicodeError, json.JSONDecodeError, RunnerError):
                    status = "invalid_response"
                break
            status = "http_error" if code else "transport_error"
            break
        expected = case.get("expected", {})
        correctness = {}
        if status == "ok":
            for qid, expected_value in expected.items():
                kind = case["questions"][qid]["type"]
                value = answers[qid][kind]
                if kind == "noul":
                    value = value >= case["thresholds"][qid]
                correctness[qid] = value == expected_value
        if status in {"unauthorized", "access_denied"}:
            denied = {"case_id": case["id"], "status": status, "attempts": attempts,
                      "latency_ms": round((time.monotonic() - started) * 1000, 3), "correctness": {}, "http_status": http_status}
            if status == "access_denied" and isinstance(response, bytes) and len(response) <= 4096 and _EDGE_1010_BODY.fullmatch(response):
                denied["diagnostic_code"] = "edge_1010"
            results.append(denied)
            break
        results.append({"case_id": case["id"], "status": status, "attempts": attempts,
                        "http_status": http_status,
                        "latency_ms": round((time.monotonic() - started) * 1000, 3),
                        "correctness": correctness, "answers": answers if status == "ok" else {},
                        "response_model": response_model, "usage": usage if status == "ok" else {}})
        if status in {"request_cap", "input_cap", "deadline"}:
            break
    cases_completed = sum(r["status"] == "ok" for r in results)
    result = {"model": experiment["model"], "results": results, "requests": request_count, "input_bytes": total,
              "cases_expected": len(cases), "cases_completed": cases_completed,
              "complete": len(results) == len(cases) and cases_completed == len(cases)}
    if target_revision is not None:
        result["target_revision"] = target_revision
    return result


def _check_output_path(path: str) -> pathlib.Path:
    target = pathlib.Path(path).absolute()
    if os.path.lexists(target):
        raise RunnerError("output file already exists")
    target = target.parent.resolve() / target.name
    ancestor = target.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    try:
        inside = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ancestor, capture_output=True, text=True).returncode == 0
        ignored = subprocess.run(["git", "check-ignore", "--quiet", str(target)], cwd=ancestor, capture_output=True).returncode == 0
        if inside and not ignored:
            raise RunnerError("output must be git-ignored inside a git repository")
    except OSError:
        raise RunnerError("git is required to check output privacy") from None
    return target


def _write_result(path: str, result: dict[str, Any]) -> None:
    target = _check_output_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(_json_bytes(result) + b"\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("status", "preview", "run"))
    parser.add_argument("--experiment", required=False)
    parser.add_argument("--policy", required=False)
    parser.add_argument("--key-file")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps({"api": API_URL, "runner": "ready", "key_configured": _key_configured(args.key_file)}, separators=(",", ":")))
            return 0
        if not args.experiment or not args.policy:
            raise RunnerError("--experiment and --policy are required")
        experiment, experiment_raw = _read_json(args.experiment)
        policy, policy_raw = _read_json(args.policy)
        if args.command == "preview":
            print(json.dumps(_preview(experiment, policy), ensure_ascii=False, separators=(",", ":")))
            return 0
        if not args.output:
            raise RunnerError("run requires --output")
        _check_output_path(args.output)
        result = _run(experiment, policy, _key(args.key_file))
        result["experiment_sha256"] = _sha(experiment_raw)
        result["policy_sha256"] = _sha(policy_raw)
        _write_result(args.output, result)
        failure_statuses = sorted({item["status"] for item in result["results"] if item["status"] != "ok"})
        print(json.dumps({"status": "complete" if result["complete"] else "incomplete",
                          "cases_expected": result["cases_expected"],
                          "cases_completed": result["cases_completed"],
                          "requests": result["requests"],
                          "failure_statuses": failure_statuses,
                          "output": args.output}, separators=(",", ":")))
        return 0 if result["complete"] else 1
    except RunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError):
        print("local input or output operation failed", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
