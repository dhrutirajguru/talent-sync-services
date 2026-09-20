import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.skill import Skill, SkillCategory, UserSkill


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Skill]:
        stmt = select(Skill).where(Skill.status == "ACTIVE").options(selectinload(Skill.category))
        return list(self.db.execute(stmt).scalars().all())

    def list_categories(self) -> list[SkillCategory]:
        stmt = select(SkillCategory).where(SkillCategory.status == "ACTIVE")
        return list(self.db.execute(stmt).scalars().all())

    def get_by_ids(self, skill_ids: list[uuid.UUID]) -> list[Skill]:
        if not skill_ids:
            return []
        stmt = select(Skill).where(Skill.id.in_(skill_ids))
        return list(self.db.execute(stmt).scalars().all())

    def get_user_skills(self, user_id: uuid.UUID) -> list[UserSkill]:
        stmt = (
            select(UserSkill)
            .where(UserSkill.user_id == user_id)
            .options(selectinload(UserSkill.skill))
        )
        return list(self.db.execute(stmt).scalars().all())

    def replace_user_skills(self, user_id: uuid.UUID, rows: list[dict]) -> None:
        """
        Full-replace: delete existing rows for this user, insert the new set.
        Simple and correct for demo scale; a real Phase-1 implementation would
        diff instead of delete/reinsert to preserve verified/assessed history.
        """
        self.db.query(UserSkill).filter(UserSkill.user_id == user_id).delete()
        for row in rows:
            self.db.add(
                UserSkill(
                    user_id=user_id,
                    skill_id=row["skill_id"],
                    proficiency_level=row["proficiency_level"],
                    years_experience=row.get("years_experience"),
                    source="SELF_DECLARED",
                )
            )
        self.db.flush()
