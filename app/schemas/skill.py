import uuid

from pydantic import BaseModel, ConfigDict, Field


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category_id: uuid.UUID | None = None
    skill_type: str | None = None


class UserSkillIn(BaseModel):
    """One row of a student's skill self-declaration/update."""

    skill_id: uuid.UUID
    proficiency_level: str = Field(description="BEGINNER | INTERMEDIATE | ADVANCED | EXPERT")
    years_experience: float | None = None


class UserSkillsUpdateRequest(BaseModel):
    """
    Full-replace update: the profile-edit screen sends the complete current
    set of skills, and the service reconciles it against what's stored
    (simpler and safer for a demo than diffing add/remove separately).
    """

    skills: list[UserSkillIn]


class UserSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: uuid.UUID
    skill_name: str
    proficiency_level: str
    years_experience: float | None = None
    verified: bool
