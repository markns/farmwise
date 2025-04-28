# validators.py


def must_not_be_blank(v: str, field_name: str = "Field") -> str:
    """Ensure a string is not empty or only whitespace."""
    if not v.strip():
        raise ValueError(f"{field_name} must not be empty or whitespace.")
    return v
