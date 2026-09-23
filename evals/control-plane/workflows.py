"""Synthetic control-plane workflows; no model or service calls."""


def find_support(query, records, read_limit=3):
    """Return inspected evidence and a draft answer from a fixed-size search."""
    terms = set(query.lower().split())
    ranked = sorted(
        records,
        key=lambda record: len(terms & set(record["text"].lower().split())),
        reverse=True,
    )
    inspected = ranked[:read_limit]
    answer = next((record["text"] for record in inspected if record["kind"] == "answer"), None)
    return {"answer": answer, "inspected_ids": [record["id"] for record in inspected]}


def ci_for_change(changed_paths, owners, run_tests):
    """Select mapped tests, retaining a full-suite fallback on failure or no map."""
    selected = sorted({test for path in changed_paths for test in owners.get(path, ())})
    if not selected:
        return {"selected": [], "full_suite": run_tests(["all"])}
    focused = run_tests(selected)
    return {
        "selected": selected,
        "focused": focused,
        "full_suite": run_tests(["all"]) if not focused else None,
    }


def task_context(task_id, current_revision, notes, cached_summaries, max_notes=2):
    """Supply bounded context to a later planner; cache key is only task ID."""
    if task_id in cached_summaries:
        return {"revision": current_revision, "context": cached_summaries[task_id], "cache_hit": True}
    latest = sorted(notes, key=lambda note: note["updated_at"], reverse=True)[:max_notes]
    return {
        "revision": current_revision,
        "context": "\n".join(note["text"] for note in latest),
        "cache_hit": False,
    }


def review_proposal(requested_terms, proposal, required_approvals):
    """Keyword coverage screens a proposal; approvals remain exact gates."""
    missing = [term for term in requested_terms if term.lower() not in proposal.lower()]
    return {
        "needs_review": bool(missing),
        "missing_terms": missing,
        "may_execute": not missing and all(required_approvals.values()),
    }
