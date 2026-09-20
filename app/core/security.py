"""
Password hashing and JWT access-token handling.

Scope note (Section 6.1, Demo Phase): only access tokens are implemented here.
The refresh_tokens table exists in the schema (see app/models/auth.py once
added) so rotation logic can be turned on in Phase 1-proper without a schema
change — but for the demo, a single longer-lived access token is enough.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings

_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """
    subject: typically the user's id (as a string).
    extra_claims: e.g. {"roles": ["STUDENT"]} — kept minimal and non-sensitive,
    since JWT payloads are base64, not encrypted.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Returns the decoded payload, or None if the token is invalid/expired."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
