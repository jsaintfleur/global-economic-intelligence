import hashlib


def stable_id(prefix: str, *parts: object) -> str:
    material = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(material.encode()).hexdigest()[:24]}"
