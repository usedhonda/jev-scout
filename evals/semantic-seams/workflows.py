"""Synthetic decision seams; no provider calls or deployed integration."""

from __future__ import annotations

import re


def account_exists(status: int, final_url: str, body: str) -> str:
    """The caller displays found/missing/unknown to a username-search user."""
    if "robot check" in body.lower():
        return "unknown"
    if status == 404 or final_url.endswith("/not-found"):
        return "missing"
    if status == 200:
        return "found"
    return "unknown"


def latest_reply(body: str) -> str:
    """A helpdesk stores this text as the customer's new answer."""
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"On .* wrote:$", line) or line.startswith(">"):
            return "\n".join(lines[:index]).strip()
    return body.strip()


def release_impact(message: str) -> str:
    """The release workflow uses this label before exact version arithmetic."""
    if "BREAKING CHANGE:" in message:
        return "major"
    if message.startswith("feat:"):
        return "minor"
    if message.startswith("fix:"):
        return "patch"
    return "none"


def memory_update(new_fact: str, old_memories: list[tuple[str, str]]) -> dict:
    """This mock LLM response mixes a closed operation/ID with generated text."""
    if not old_memories:
        return {"event": "ADD", "target_id": None, "memory_text": new_fact}
    memory_id, old_text = old_memories[0]
    if new_fact.lower() == old_text.lower():
        return {"event": "NONE", "target_id": memory_id, "memory_text": ""}
    return {"event": "UPDATE", "target_id": memory_id, "memory_text": new_fact}


def should_close_issue(days_idle: int, comments: list[tuple[str, str]]) -> bool:
    """The bot closes the issue; comments are (role, text) pairs."""
    if days_idle < 30:
        return False
    return True


def format_canonical(source: str) -> str:
    """For a fixed mode this tool promises the same output on every run."""
    return "\n".join(line.rstrip() for line in source.splitlines()).strip() + "\n"


def indistinguishable_account_pages(claimed: bool) -> tuple[int, str]:
    """The available response deliberately contains no evidence of claimed."""
    _ = claimed
    return 200, "Please sign in to continue"
