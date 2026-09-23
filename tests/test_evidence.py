import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals/evidence"))
from decisions import validate_candidates, resolve, placement_replay


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.source = "Use the reset menu."
        self.candidates = [{"id": "d1", "kind": "doc", "text": self.source, "start": 0, "end": len(self.source)}]

    def row(self, evidence="d1", decision="already_answered"):
        return {"status": "ok", "answers": {"decision": {"choice": decision, "confidence": .95}, "evidence": {"choice": evidence, "confidence": .95}}}

    def test_correction_retains_original_and_does_not_claim_truth(self):
        out = resolve(self.source, self.candidates, self.row())
        self.assertEqual(out["proposed"], "already_answered")
        self.assertEqual(out["final"], "answerable_by_docs")
        self.assertEqual(out["reason"], "source_type_correction")

    def test_missing_omitted_and_service_failure_are_separate(self):
        for candidate in ("none", "outside"):
            self.assertEqual(resolve(self.source, self.candidates, self.row(candidate))["reason"], "missing_evidence")
        self.assertEqual(resolve(self.source, [], self.row())["reason"], "missing_evidence")
        self.assertEqual(resolve(self.source, self.candidates, None)["reason"], "provider_failure")
        self.assertEqual(resolve(self.source, self.candidates, self.row("none", "needs_human"))["reason"], "abstain")

    def test_provenance_mismatch_fails_before_resolution(self):
        with self.assertRaises(ValueError):
            validate_candidates("Changed source", self.candidates)
        with self.assertRaises(ValueError):
            validate_candidates(self.source, self.candidates * 2)

    def test_selective_placement_includes_confident_baseline_errors(self):
        items = [{"hits": ["wrong"], "recorded_choice": "right", "expected": "right"},
                 {"hits": [], "recorded_choice": "right", "expected": "right"},
                 {"hits": ["a", "b"], "recorded_choice": "right", "expected": "right"}]
        result = placement_replay(items)
        self.assertEqual(result["always"], {"correct": 3, "selected_cases": 3, "total": 3})
        self.assertEqual(result["no_hit"]["correct"], 1)
        self.assertEqual(result["conflict"]["correct"], 1)

    def test_unavailable_answers_are_not_model_accuracy(self):
        import hashlib
        import importlib.util
        import json
        import tempfile
        directory = Path(__file__).resolve().parents[1] / "evals/evidence"
        spec = importlib.util.spec_from_file_location("evidence_compare", directory / "compare.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        raw = (directory / "experiment.json").read_bytes()
        result = {"experiment_sha256": hashlib.sha256(raw).hexdigest(), "results": [
            {"case_id": c["id"], "status": "http_error"} for c in json.loads(raw)["cases"]]}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "result.json"
            path.write_text(json.dumps(result))
            summary = module.compare(path)
        self.assertEqual(summary["valid_cases"], 0)
        self.assertIsNone(summary["raw_correct"])
        self.assertIsNone(summary["final_correct"])
        self.assertIsNone(summary["placement_replay"])
        self.assertIsNone(summary["reported_usage"])


if __name__ == "__main__":
    unittest.main()
