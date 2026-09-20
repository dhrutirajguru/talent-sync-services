import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email, User.deleted_at.is_(None))
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, *, email: str, password_hash: str, first_name: str, last_name: str | None) -> User:
        user = User(email=email, password_hash=password_hash, first_name=first_name, last_name=last_name)
        self.db.add(user)
        self.db.flush()
        return user

    def assign_role(self, user: User, role: Role) -> None:
        self.db.add(UserRole(user_id=user.id, role_id=role.id))


    def list_by_role(self, role_code: str) -> list[User]:
        stmt = (
            select(User)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.code == role_code, User.deleted_at.is_(None))
        )
        return list(self.db.execute(stmt).scalars().all())


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code)
        return self.db.execute(stmt).scalar_one_or_none()
