"""Optional typed decision integration; no service credentials in application data."""
from baseline import route


def route_ticket(text, provider=None, minimum_confidence=0.9):
    fallback = route(text)
    if provider is None:
        return fallback
    try:
        answer = provider(text)
        choice = answer["choice"]
        confidence = answer["confidence"]
        if (choice in {"billing", "technical", "general"}
                and isinstance(confidence, (int, float))
                and not isinstance(confidence, bool)
                and minimum_confidence <= confidence <= 1):
            return choice
    except (TimeoutError, ConnectionError, KeyError, TypeError, ValueError):
        pass
    return fallback
