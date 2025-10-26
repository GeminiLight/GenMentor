from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple, TypeAlias
from pydantic import BaseModel, Field, field_validator
from base import BaseAgent
from .prompts.skill_gap_identifier import (
    skill_gap_identifier_system_prompt,
    skill_gap_identifier_task_prompt_goal2skill,
    skill_gap_identifier_task_prompt_identification,
)
from .schemas import SkillRequirements, SkillGaps

JSONDict: TypeAlias = Dict[str, Any]


class Goal2SkillPayload(BaseModel):
    """Payload for mapping a learning goal to required skills (validated)."""

    learning_goal: str = Field(...)


class SkillGapPayload(BaseModel):
    """Payload for identifying skill gaps (validated)."""

    learning_goal: str = Field(...)
    learner_information: str = Field(...)
    skill_requirements: Dict[str, Any] = Field(...)


class ReflexionPayload(BaseModel):
    """Payload for reflexion on goal-to-skill mapping (validated)."""

    learning_goal: str = Field(...)
    learner_information: str = Field(...)
    previous_skill_requirements: Dict[str, Any] = Field(...)


class SkillGapIdentifier(BaseAgent):
    """Agent wrapper for skill requirement discovery and gap identification."""

    name: str = "SkillGapIdentifier"

    def __init__(self, model: Any, ) -> None:
        super().__init__(
            model=model,
            system_prompt=skill_gap_identifier_system_prompt,
            jsonalize_output=True,
        )

    def map_goal_to_skill(
        self,
        input_dict: Mapping[str, Any],
    ) -> JSONDict:
        """Map a learner's goal to the set of required skills."""
        task_prompt = skill_gap_identifier_task_prompt_goal2skill
        payload_dict = Goal2SkillPayload(**input_dict).model_dump()
        raw_output = self.invoke(payload_dict, task_prompt=task_prompt)
        validated = SkillRequirements.model_validate(raw_output)
        return validated.model_dump()

    def identify_skill_gap(
        self,
        input_dict: Mapping[str, Any],
    ) -> JSONDict:
        """Identify knowledge gaps using learner information and expected skills."""
        payload_dict = SkillGapPayload(**input_dict).model_dump()
        task_prompt = skill_gap_identifier_task_prompt_identification
        raw_output = self.invoke(payload_dict, task_prompt=task_prompt)
        validated = SkillGaps.model_validate(raw_output)
        return validated.model_dump()

    def reflexion(
        self,
        input_dict: Mapping[str, Any],
    ) -> JSONDict:
        """Refine an existing goal-to-skill mapping using feedback signals."""
        payload_dict = ReflexionPayload(**input_dict).model_dump()
        task_prompt = skill_gap_identifier_task_prompt_goal2skill
        raw_output = self.invoke(payload_dict, task_prompt=task_prompt)
        validated = SkillRequirements.model_validate(raw_output)
        return validated.model_dump()


def map_goal_to_skills_with_llm(llm: Any, learning_goal: str) -> JSONDict:
    """Convenience wrapper to map a goal to required skills using the provided LLM."""

    skill_gap_identifier = SkillGapIdentifier(llm)
    return skill_gap_identifier.map_goal_to_skill({"learning_goal": learning_goal})


def identify_skill_gap_with_llm(
    llm: Any,
    learning_goal: str,
    learner_information: str,
) -> Tuple[JSONDict, JSONDict]:
    """Identify skill gaps and return both the gaps and the skill requirements used."""

    skill_gap_identifier = SkillGapIdentifier(llm)

    effective_requirements = skill_gap_identifier.map_goal_to_skill(
        {
            "learning_goal": learning_goal,
        },
    )

    skill_gap = skill_gap_identifier.identify_skill_gap(
        {
            "learning_goal": learning_goal,
            "learner_information": learner_information,
            "skill_requirements": effective_requirements,
        },
    )
    return skill_gap, effective_requirements

if __name__ == "__main__":
    # python -m modules.skill_gap_identification.skill_gap_identifier
    from base.llm_factory import LLMFactory

    llm = LLMFactory.create(model="deepseek-chat", model_provider="deepseek")

    learning_goal = "Become proficient in data science."
    learner_information = "I have a background in statistics but limited programming experience."

    skill_gap, skill_requirements = identify_skill_gap_with_llm(
        llm,
        learning_goal,
        learner_information,
    )

    print("Identified Skill Gap:", skill_gap)
    print("Skill Requirements Used:", skill_requirements)