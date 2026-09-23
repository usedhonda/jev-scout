"""Synthetic exploratory surfaces; intentionally small and offline."""

import hashlib


def retrieve_notes(query, notes, limit=4):
    """Classical word-overlap prior produces a shortlist for the researcher."""
    terms = set(query.lower().split())
    return sorted(
        notes,
        key=lambda note: len(terms & set(note["text"].lower().split())),
        reverse=True,
    )[:limit]


def beam_route(start_id, goal_id, graph, labels, goal_text, width=2, depth_limit=4):
    """Order legal search branches by word overlap; prove the goal by exact ID."""
    terms = set(goal_text.lower().split())
    frontier = [(start_id, 0, (start_id,))]
    for depth in range(depth_limit + 1):
        for node_id, cost, path in frontier:
            if node_id == goal_id:
                return {"path": path, "cost": cost}
        if depth == depth_limit:
            break
        candidates = [
            (child_id, cost + edge_cost, path + (child_id,))
            for node_id, cost, path in frontier
            for child_id, edge_cost in graph.get(node_id, ())
            if child_id not in path
        ]
        frontier = sorted(
            candidates,
            key=lambda branch: (
                -len(terms & set(labels[branch[0]].lower().split())),
                branch[1],
            ),
        )[:width]
    return None


def choose_draft(drafts):
    """Best-of-N generation has an independent-looking but shallow evaluator."""
    return max(drafts, key=lambda draft: draft.count("source:"), default=None)


def next_step(goal, target_ids):
    """Two factorized choices feed a deterministic tool dispatcher."""
    verb = "inspect" if "check" in goal.lower() else "summarize"
    target = next((target_id for target_id in target_ids if target_id.lower() in goal.lower()), None)
    return {"operation": verb, "target_id": target} if target else None


def parse_command(text, allowed_ids):
    """A finite grammar is exact and already sufficient for this surface."""
    parts = text.lower().split()
    if len(parts) == 2 and parts[0] in {"inspect", "summarize"} and parts[1] in allowed_ids:
        return {"operation": parts[0], "target_id": parts[1]}
    return None


def utterance_complete(transcript, silence_ms):
    """A fixed pause ends capture even if the speaker is about to continue."""
    return silence_ms >= 700


def emergency_stop(stop_button_pressed):
    """Hard real-time local stop; no remote inference is on this path."""
    return bool(stop_button_pressed)


def artifact_matches(payload, expected_sha256):
    """Exact integrity proof; semantic similarity is not a substitute."""
    return hashlib.sha256(payload).hexdigest() == expected_sha256
