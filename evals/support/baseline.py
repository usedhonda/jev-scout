def route(text):
    lowered = text.lower()
    if "refund" in lowered or "invoice" in lowered:
        return "billing"
    if "crash" in lowered or "error" in lowered:
        return "technical"
    return "general"


def improved_route(text):
    if any(word in text for word in ("二重", "請求", "返金")):
        return "billing"
    if any(word in text for word in ("起動", "落ち", "エラー")):
        return "technical"
    return route(text)
