import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class OpportunitySkillIn(BaseModel):
    skill_id: uuid.UUID
    required_level: str | None = None
    importance: str = "MEDIUM"
    required: bool = True


class OpportunityCreate(BaseModel):
    title: str
    opportunity_type: str = Field(description="INTERNSHIP | JOB | APPRENTICESHIP | ...")
    description: str
    department: str | None = None
    location: str | None = None
    work_mode: str | None = None
    duration_text: str | None = None
    stipend_amount: float | None = None
    application_deadline: datetime | None = None
    start_date: date | None = None
    end_date: date | None = None
    eligibility_criteria: str | None = None
    min_cgpa: float | None = None
    openings_count: int | None = None
    required_skills: list[OpportunitySkillIn] = []


class OpportunitySkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: uuid.UUID
    skill_name: str
    required_level: str | None = None
    importance: str
    required: bool


class OpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    organization_name: str
    title: str
    opportunity_type: str
    description: str
    location: str | None = None
    work_mode: str | None = None
    status: str
    required_skills: list[OpportunitySkillOut] = []


class OpportunityMatchOut(OpportunityOut):
    """Student-facing: an opportunity plus how well it matches their skill profile."""

    match_score: float = Field(description="0.0-1.0, fraction of required skills the student has")
    matched_skill_names: list[str] = []
    missing_skill_names: list[str] = []


class CandidateMatchOut(BaseModel):
    """Industry-facing: a student ranked against one opportunity's required skills."""

    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    first_name: str
    last_name: str | None = None
    email: str
    match_score: float
    matched_skill_names: list[str] = []
    missing_skill_names: list[str] = []
    has_applied: bool = False
