from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token.")

    user = UserRepository(db).get_by_id(payload["sub"])
    if user is None or user.status != "ACTIVE":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive.")
    return user


def require_role(role_code: str):
    """
    Dependency factory for simple role-based route guards (Section 2.2's
    NFR notes: fine-grained permission tables are explicitly deferred —
    role checks in the API layer are enough for the demo).
    """

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if role_code not in current_user.role_codes:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, f"This action requires the '{role_code}' role."
            )
        return current_user

    return _dependency
