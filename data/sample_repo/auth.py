def validate_token(token: str) -> bool:
    """Minimal example authentication check."""
    return bool(token and token.startswith("demo_"))
