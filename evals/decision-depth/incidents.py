"""Synthetic incident intake, with an injected notification consumer."""

from decimal import Decimal


def route_report(text):
    """Current deterministic routing; unrecognized reports wait for review."""
    lowered = text.lower()
    if "breach" in lowered or "leak" in lowered:
        return "security"
    if "billing" in lowered or "invoice" in lowered:
        return "billing"
    if "outage" in lowered or "down" in lowered:
        return "operations"
    return "review"


def accept_report(report, notify_security):
    """Persist a route and notify the security desk for that route only."""
    route = route_report(report["text"])
    stored = {"id": report["id"], "text": report["text"], "route": route}
    if route == "security":
        notify_security(stored)
    return stored


def invoice_total(line_items):
    return sum((Decimal(str(item["unit_price"])) * item["quantity"]
                for item in line_items), Decimal("0"))


def can_read_report(user_id, allowed_user_ids):
    return user_id in allowed_user_ids
