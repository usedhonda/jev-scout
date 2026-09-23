"""Example-specific evidence invariant. This is not part of the API runner."""


def validate_candidates(source, candidates):
    ids = set()
    for item in candidates:
        start, end = item["start"], item["end"]
        if (item["id"] == "none" or item["id"] in ids or
                type(start) is not int or type(end) is not int or
                not 0 <= start < end <= len(source) or source[start:end] != item["text"] or
                item["kind"] not in {"message", "doc"}):
            raise ValueError("Candidate does not match source")
        ids.add(item["id"])


def resolve(source, candidates, row):
    validate_candidates(source, candidates)
    if row is None or row.get("status") != "ok":
        return {"proposed": None, "evidence": None, "final": "needs_human", "reason": "provider_failure"}
    answers = row["answers"]
    proposed = answers["decision"]["choice"]
    selected = answers["evidence"]["choice"]
    result = {"proposed": proposed, "evidence": selected, "final": "needs_human", "reason": "missing_evidence"}
    if proposed not in {"already_answered", "answerable_by_docs", "needs_human"}:
        result["reason"] = "invalid_decision"
        return result
    if proposed == "needs_human":
        result["reason"] = "abstain"
        return result
    evidence = next((c for c in candidates if c["id"] == selected), None)
    if evidence is None:
        return result
    # A demo threshold, not calibrated production policy.
    if any(answers[q]["confidence"] < .8 for q in ("decision", "evidence")):
        result["reason"] = "uncertain"
        return result
    result["final"] = "already_answered" if evidence["kind"] == "message" else "answerable_by_docs"
    result["reason"] = "consistent" if result["final"] == proposed else "source_type_correction"
    return result


def placement_replay(items):
    """Compare routes on recorded answers; no network or cost/latency estimate."""
    result = {}
    for mode in ("never", "always", "no_hit", "conflict"):
        correct = calls = 0
        for item in items:
            hits = item["hits"]
            baseline = hits[0] if len(hits) == 1 else "review"
            use = mode == "always" or (mode == "no_hit" and not hits) or (mode == "conflict" and len(hits) > 1)
            calls += int(use)
            output = item["recorded_choice"] if use else baseline
            correct += output == item["expected"]
        result[mode] = {"correct": correct, "selected_cases": calls, "total": len(items)}
    return result
