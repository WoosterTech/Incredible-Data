def display_name(user) -> str:
    """Return user's display name."""
    return user.name or user.email
