"""Synthetic repository surfaces for discovery, not production code."""
import re
from datetime import date


def rule_matches(value, rule):
    if rule["type"] == "exact":
        return value == rule["value"]
    if rule["type"] == "greater":
        return value > rule["value"]
    if rule["type"] == "regex":
        return re.search(rule["value"], value) is not None
    raise ValueError("Unknown rule")


def changed_notification(before, after, trigger):
    if before == after:
        return None
    return {"before": before, "after": after} if trigger in after else None


def suggested_labels(title, rules, explicit):
    if explicit:
        return explicit
    hits = {label for pattern, label in rules if re.search(pattern, title)}
    return hits if len(hits) == 1 else {"review"}


def document_assignment(text, classify, corrections):
    if text in corrections:
        return corrections[text]
    return classify(text)


def review_order(items):
    return sorted(items, key=lambda item: item["changed_lines"], reverse=True)


def date_candidates(text):
    return [{"id": str(i), "value": match[0], "start": match.start(), "end": match.end()}
            for i, match in enumerate(re.finditer(r"\d{4}-\d{2}-\d{2}", text))]


def first_date(text):
    candidates = date_candidates(text)
    return candidates[0] if candidates else None


def answer_source(question, sources):
    return next((s for s in sources if question.lower() in s["text"].lower()), None)


def compare_versions(left, right):
    # This miniature format deliberately supports three numeric components only.
    def parse(value):
        if not re.fullmatch(r"\d+\.\d+\.\d+", value):
            raise ValueError("Invalid version")
        return tuple(map(int, value.split(".")))
    a, b = parse(left), parse(right)
    return (a > b) - (a < b)


def authorized(user_id, allowed_ids):
    return user_id in allowed_ids


def route_ticket(destination, urgent=False):
    # destination is one of "billing", "engineering", "general"
    return {"queue": destination, "urgent": bool(urgent)}


def dispatch_request(text):
    lowered = text.lower()
    destination = "billing" if "refund" in lowered else "engineering" if "error" in lowered else "general"
    return route_ticket(destination, urgent="asap" in lowered)


def due_soon(text, today):
    candidates = date_candidates(text)
    if not candidates:
        return None
    return (date.fromisoformat(candidates[0]["value"]) - today).days <= 7


def hide_comment(comment):
    return any(word in comment.lower() for word in ("scam", "idiot"))


def needs_escalation(command):
    return "credentials" in command or "auth" in command


def churn_features(review):
    lowered = review.lower()
    return [int("cancel" in lowered), int("expensive" in lowered), lowered.count("!")]
