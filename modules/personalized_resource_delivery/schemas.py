from __future__ import annotations

from enum import Enum
from typing import List, Sequence

from pydantic import BaseModel, Field, RootModel, field_validator


class Proficiency(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class DesiredOutcome(BaseModel):
    name: str = Field(..., description="Skill name")
    level: Proficiency = Field(..., description="Desired proficiency when completed")


class SessionItem(BaseModel):
    id: str = Field(..., description="Session identifier, e.g., 'Session 1'")
    title: str
    abstract: str
    if_learned: bool
    associated_skills: List[str] = Field(default_factory=list)
    desired_outcome_when_completed: List[DesiredOutcome] = Field(default_factory=list)

    @field_validator("associated_skills")
    @classmethod
    def ensure_nonempty_strings(cls, v: Sequence[str]) -> List[str]:
        return [s for s in (str(x).strip() for x in v) if s]


class LearningPath(RootModel[List[SessionItem]]):
    root: List[SessionItem]

    @field_validator("root")
    @classmethod
    def limit_sessions(cls, v: List[SessionItem]) -> List[SessionItem]:
        # Per prompt, 1..10 sessions
        if not (1 <= len(v) <= 10):
            raise ValueError("Learning path must contain between 1 and 10 sessions.")
        return v


class LearningPathResult(BaseModel):
    tracks: List[str] = Field(default_factory=list)
    result: LearningPath


def parse_learning_path_result(data) -> LearningPathResult:
    """Validate scheduler output into a structured model."""
    return LearningPathResult.model_validate(data)
