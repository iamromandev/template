"""Custom validators reused across request DTOs."""

from __future__ import annotations

import re

# OWASP 2024 password guidance: ≥12 chars, no composition rules
_PASSWORD_MIN_LEN = 12
_PASSWORD_RE = re.compile(r"^[!-~]+$")  # printable ASCII, no whitespace


class PasswordValidationError(ValueError):
    """Raised when a password fails one of the policy checks."""


def validate_password(password: str) -> None:
    """Raise ``PasswordValidationError`` if ``password`` violates policy."""
    if len(password) < _PASSWORD_MIN_LEN:
        raise PasswordValidationError(f"Password must be at least {_PASSWORD_MIN_LEN} characters")
    if not _PASSWORD_RE.match(password):
        raise PasswordValidationError("Password must contain only printable ASCII (no whitespace)")
    # Cheap complexity hint — not a hard requirement, but warn-worthy.
    classes = sum(
        [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ]
    )
    if classes < 3:
        raise PasswordValidationError("Password must contain at least 3 of: lowercase, uppercase, digit, symbol")


__all__ = ["PasswordValidationError", "validate_password"]
