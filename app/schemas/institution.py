import uuid

from pydantic import BaseModel


class SkillGapItem(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    demand_count: int  # how many live opportunities require this skill
    supply_count: int  # how many of the institution's students have it
    gap_score: int      # demand_count - supply_count; higher = bigger gap


class SkillGapReportOut(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
    total_students: int
    gaps: list[SkillGapItem]
