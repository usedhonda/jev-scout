"""Offline comparison of saved judgments; never performs API calls."""
import argparse
import hashlib
import json
from pathlib import Path
from decisions import resolve, placement_replay, validate_candidates


def compare(path):
    raw = Path(__file__).with_name("experiment.json").read_bytes()
    experiment = json.loads(raw)
    result = json.loads(Path(path).read_text())
    if result.get("experiment_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("Result belongs to another experiment")
    rows = {r["case_id"]: r for r in result["results"]}
    corrected = good_before = good_after = 0
    valid = 0
    selected = []
    outcomes = []
    for case in experiment["cases"]:
        state = case["state"]
        validate_candidates(state["source"], state["candidates"])
        row = rows.get(case["id"])
        out = resolve(state["source"], state["candidates"], row)
        available = row is not None and row.get("status") == "ok"
        if available:
            valid += 1
            good_before += out["proposed"] == case["expected"]["decision"]
            good_after += out["final"] == case["expected"]["decision"]
            corrected += out["reason"] == "source_type_correction"
        outcomes.append({"case_id": case["id"], **out})
        selected.append({"hits": case["baseline_hits"], "recorded_choice": out["final"], "expected": case["expected"]["decision"]})
    return {"cases": len(experiment["cases"]), "valid_cases": valid,
            "raw_correct": good_before if valid else None, "final_correct": good_after if valid else None,
            "corrections": corrected, "outcomes": outcomes,
            "placement_replay": placement_replay(selected) if valid == len(experiment["cases"]) else None,
            "reported_usage": {k: sum(r.get("usage", {}).get(k, 0) for r in rows.values()) for k in ("input_tokens", "output_tokens")} if valid else None,
            "evidence": "Synthetic judgments and offline replay; no measured billing or latency savings"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    print(json.dumps(compare(args.result), ensure_ascii=False))
