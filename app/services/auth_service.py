import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.organization_repository import ProfileRepository
from app.repositories.user_repository import RoleRepository, UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)
        self.profiles = ProfileRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        if self.users.get_by_email(payload.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists.")

        role = self.roles.get_by_code(payload.role_code)
        if role is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown role_code '{payload.role_code}'.")

        user = self.users.create(
            email=payload.email,
            password_hash=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        self.users.assign_role(user, role)

        org_id = uuid.UUID(payload.organization_id) if payload.organization_id else None
        if payload.role_code == "STUDENT":
            self.profiles.create_student_profile(user.id, institution_id=org_id)
        elif payload.role_code == "ACADEMICIAN":
            self.profiles.create_academician_profile(user.id, institution_id=org_id)
        elif payload.role_code == "INDUSTRY":
            self.profiles.create_industry_profile(user.id, organization_id=org_id)

        self.db.commit()
        return self.users.get_by_id(user.id)

    def login(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")

        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

        return create_access_token(subject=str(user.id), extra_claims={"roles": user.role_codes})
