import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.profile import AcademicianProfile, IndustryProfile, StudentProfile


class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, org_id: uuid.UUID) -> Organization | None:
        return self.db.get(Organization, org_id)

    def list_by_type(self, organization_type: str) -> list[Organization]:
        stmt = select(Organization).where(
            Organization.organization_type == organization_type,
            Organization.deleted_at.is_(None),
        )
        return list(self.db.execute(stmt).scalars().all())


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_student_profile(self, user_id: uuid.UUID, institution_id: uuid.UUID | None) -> StudentProfile:
        profile = StudentProfile(user_id=user_id, institution_id=institution_id)
        self.db.add(profile)
        self.db.flush()
        return profile

    def create_academician_profile(self, user_id: uuid.UUID, institution_id: uuid.UUID | None) -> AcademicianProfile:
        profile = AcademicianProfile(user_id=user_id, institution_id=institution_id)
        self.db.add(profile)
        self.db.flush()
        return profile

    def create_industry_profile(self, user_id: uuid.UUID, organization_id: uuid.UUID | None) -> IndustryProfile:
        profile = IndustryProfile(user_id=user_id, organization_id=organization_id)
        self.db.add(profile)
        self.db.flush()
        return profile

    def get_student_profile(self, user_id: uuid.UUID) -> StudentProfile | None:
        stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_academician_profile(self, user_id: uuid.UUID) -> AcademicianProfile | None:
        stmt = select(AcademicianProfile).where(AcademicianProfile.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_industry_profile(self, user_id: uuid.UUID) -> IndustryProfile | None:
        stmt = select(IndustryProfile).where(IndustryProfile.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
