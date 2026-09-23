"""Compare frozen synthetic labels; optionally replay real runner responses in app."""
import argparse
import json
from pathlib import Path

from baseline import route, improved_route
from app import route_ticket


def compare(result_path=None):
    experiment = json.loads(Path(__file__).with_name("experiment.json").read_text())
    cases = experiment["cases"]
    summary = {"dataset": experiment["revision"], "count": len(cases)}
    for name, function in (("baseline", route), ("dictionary", improved_route)):
        summary[name + "_correct"] = sum(function(c["state"]["text"]) == c["expected"]["queue"] for c in cases)
    if result_path:
        import hashlib
        result = json.loads(Path(result_path).read_text())
        digest = hashlib.sha256(Path(__file__).with_name("experiment.json").read_bytes()).hexdigest()
        if result.get("experiment_sha256") != digest:
            raise ValueError("Result belongs to another experiment")
        rows = {r["case_id"]: r for r in result["results"] if r["status"] == "ok"}
        summary["api_valid_cases"] = len(rows)
        summary["jev_correct"] = sum(rows[c["id"]]["correctness"].get("queue", False) for c in cases if c["id"] in rows)
        summary["app_replay_correct"] = sum(
            route_ticket(c["state"]["text"], lambda _, row=rows[c["id"]]: row["answers"]["queue"]) == c["expected"]["queue"]
            for c in cases if c["id"] in rows)
        summary["input_tokens"] = sum(r.get("usage", {}).get("input_tokens", 0) for r in rows.values())
        summary["output_tokens"] = sum(r.get("usage", {}).get("output_tokens", 0) for r in rows.values())
        summary["api_latency_ms"] = [r["latency_ms"] for r in rows.values()]
        summary["actual_models"] = sorted({r["response_model"] for r in rows.values()})
        summary["evidence"] = "Synthetic API smoke plus recorded-answer app replay, not live application E2E or production accuracy"
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result")
    args = parser.parse_args()
    print(json.dumps(compare(args.result), ensure_ascii=False))
