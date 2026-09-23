import hashlib


def verify(payload: bytes, expected: str) -> bool:
    return hashlib.sha256(payload).hexdigest() == expected
