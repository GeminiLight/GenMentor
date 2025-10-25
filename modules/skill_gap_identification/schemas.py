from enum import Enum
from typing import List
from pydantic import BaseModel, Field, ValidationError, RootModel, field_validator, constr


# ---------------------------
# Enums for controlled fields
# ---------------------------

class LevelRequired(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LevelCurrent(str, Enum):
    unlearned = "unlearned"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ---------------------------
# Output schemas
# ---------------------------

# 1) Skill Requirements
class SkillRequirement(BaseModel):
    name: str = Field(
        ...,
        description="Actionable skill name (concise, non-broad)."
    )
    required_level: LevelRequired = Field(
        ...,
        description="Proficiency level required to achieve the goal."
    )


class SkillRequirements(RootModel[List[SkillRequirement]]):
    """
    Output is a JSON array of skill requirement objects.
    Example:
    [
      {"name": "Supervised learning fundamentals", "required_level": "intermediate"},
      {"name": "Model evaluation & metrics", "required_level": "intermediate"}
    ]
    """
    root: List[SkillRequirement]

    @field_validator('root')
    @classmethod
    def limit_length_and_uniqueness(cls, v: List[SkillRequirement]):
        # Enforce 1–10 skills and unique names (case-insensitive)
        if not (1 <= len(v) <= 10):
            raise ValueError("Number of skill requirements must be within 1 to 10.")
        seen = set()
        for item in v:
            key = item.name.strip().lower()
            if key in seen:
                raise ValueError(f'Duplicate skill name detected: "{item.name}".')
            seen.add(key)
        return v


# 2) Skill Gaps
class SkillGap(BaseModel):
    name: str = Field(
        ...,
        description="Skill name matching the mapped requirement."
    )
    is_gap: bool = Field(
        ...,
        description="True if current_level is below required_level, else false."
    )
    required_level: LevelRequired = Field(
        ...,
        description="Required proficiency level."
    )
    current_level: LevelCurrent = Field(
        ...,
        description="Learner's current proficiency level."
    )
    reason: constr(strip_whitespace=True, min_length=1, max_length=160) = Field(
        ...,
        description="≤20 words concise rationale for current level."
    )
    level_confidence: Confidence = Field(
        ...,
        description="Confidence in level assessment."
    )

    @field_validator("reason")
    @classmethod
    def limit_reason_words(cls, v: str) -> str:
        # Enforce approximately ≤ 20 words
        words = v.split()
        if len(words) > 20:
            raise ValueError("Reason must be 20 words or fewer.")
        return v

    @field_validator("is_gap")
    @classmethod
    def check_gap_consistency(cls, is_gap_value, info):
        # Ensure is_gap aligns with required_level vs current_level ordering
        # order: unlearned < beginner < intermediate < advanced
        data = info.data
        required = data.get("required_level")
        current = data.get("current_level")
        if required is None or current is None:
            return is_gap_value

        order = {
            "unlearned": 0,
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
        }
        gap_should_be = order[current.value] < order[required.value]
        if is_gap_value != gap_should_be:
            raise ValueError(
                f'is_gap inconsistency: required="{required.value}", '
                f'current="{current.value}" implies is_gap={gap_should_be}.'
            )
        return is_gap_value


class SkillGaps(RootModel[List[SkillGap]]):
    """
    Output is a JSON array of skill gap objects.
    Example:
    [
      {
        "name": "Model evaluation & metrics",
        "is_gap": true,
        "required_level": "intermediate",
        "current_level": "beginner",
        "reason": "Limited hands-on projects; unfamiliar with ROC/AUC.",
        "level_confidence": "medium"
      }
    ]
    """
    root: List[SkillGap]

    @field_validator('root')
    @classmethod
    def limit_length_and_names(cls, v: List[SkillGap]):
        if not (1 <= len(v) <= 10):
            raise ValueError("Number of skill gaps must be within 1 to 10.")
        # Recommend unique names
        seen = set()
        for item in v:
            key = item.name.strip().lower()
            if key in seen:
                raise ValueError(f'Duplicate skill name detected: "{item.name}".')
            seen.add(key)
        return v


# 3) Refined Learning Goal
class RefinedLearningGoal(BaseModel):
    content: str = Field(
        ...,
        description="Refined goal text only."
    )


# ---------------------------
# Parsing helpers
# ---------------------------

def parse_skill_requirements(json_data) -> SkillRequirements:
    """
    Parse and validate the Skill Requirements array (JSON -> SkillRequirements).
    Accepts a Python object (already parsed JSON) or a JSON string.
    """
    try:
        return SkillRequirements.model_validate(json_data)
    except ValidationError as e:
        raise ValueError(f"Invalid Skill Requirements output: {e}") from e


def parse_skill_gaps(json_data) -> SkillGaps:
    """
    Parse and validate the Skill Gaps array (JSON -> SkillGaps).
    Accepts a Python object (already parsed JSON) or a JSON string.
    """
    try:
        return SkillGaps.model_validate(json_data)
    except ValidationError as e:
        raise ValueError(f"Invalid Skill Gaps output: {e}") from e


def parse_refined_learning_goal(json_data) -> RefinedLearningGoal:
    """
    Parse and validate the Refined Learning Goal object (JSON -> RefinedLearningGoal).
    Accepts a Python object (already parsed JSON) or a JSON string.
    """
    try:
        return RefinedLearningGoal.model_validate(json_data)
    except ValidationError as e:
        raise ValueError(f"Invalid Refined Learning Goal output: {e}") from e


# ---------------------------
# Example minimal tests
# ---------------------------

if __name__ == "__main__":
    # 1) Skill Requirements example
    req_ok = [
        {"name": "Supervised learning fundamentals", "required_level": "intermediate"},
        {"name": "Model evaluation & metrics", "required_level": "intermediate"},
    ]
    print(parse_skill_requirements(req_ok).model_dump())

    # 2) Skill Gaps example (consistent is_gap)
    gaps_ok = [
        {
            "name": "Model evaluation & metrics",
            "is_gap": True,
            "required_level": "intermediate",
            "current_level": "beginner",
            "reason": "Knows accuracy only; lacks ROC/AUC and calibration.",
            "level_confidence": "medium",
        }
    ]
    print(parse_skill_gaps(gaps_ok).model_dump())

    # 3) Refined learning goal example
    goal_ok = {"content": "Build a binary classifier and evaluate with ROC-AUC and F1 on a small dataset."}
    print(parse_refined_learning_goal(goal_ok).model_dump())