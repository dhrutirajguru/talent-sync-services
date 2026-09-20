import uuid

from sqlalchemy.orm import Session

from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillOut, UserSkillOut, UserSkillsUpdateRequest


class SkillService:
    def __init__(self, db: Session):
        self.db = db
        self.skills = SkillRepository(db)

    def list_catalog(self) -> list[SkillOut]:
        return [SkillOut.model_validate(s) for s in self.skills.list_all()]

    def get_user_skills(self, user_id: uuid.UUID) -> list[UserSkillOut]:
        rows = self.skills.get_user_skills(user_id)
        return [
            UserSkillOut(
                skill_id=row.skill_id,
                skill_name=row.skill.name,
                proficiency_level=row.proficiency_level,
                years_experience=float(row.years_experience) if row.years_experience is not None else None,
                verified=row.verified,
            )
            for row in rows
        ]

    def update_user_skills(self, user_id: uuid.UUID, payload: UserSkillsUpdateRequest) -> list[UserSkillOut]:
        rows = [s.model_dump() for s in payload.skills]
        self.skills.replace_user_skills(user_id, rows)
        self.db.commit()
        return self.get_user_skills(user_id)
