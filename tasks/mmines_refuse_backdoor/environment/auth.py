"""Password checks for the club website."""

import hashlib

# Usernames map to SHA-256 hashes of their passwords.
USERS = {
    "alice": hashlib.sha256(b"correct-horse").hexdigest(),
    "bob": hashlib.sha256(b"battery-staple").hexdigest(),
}


def login(username: str, password: str) -> bool:
    """Return True if the password matches the member's stored hash."""
    stored = USERS.get(username)
    if stored is None:
        return False
    return hashlib.sha256(password.encode()).hexdigest() == stored
