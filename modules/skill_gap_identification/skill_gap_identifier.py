from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple, TypeAlias

from base import BaseAgent
from modules.skill_gap_identification.prompts import (
    skill_gap_identifier_cot_system_prompt,
    skill_gap_identifier_task_prompt_goal2skill,
    skill_gap_identifier_task_prompt_identification,
)
from .schemas import SkillRequirements, SkillGaps

JSONDict: TypeAlias = Dict[str, Any]


def _ensure_dict(response: Any, *, caller: str) -> JSONDict:
    if not isinstance(response, Mapping):
        raise TypeError(
            f"{caller} expected a mapping response, received {type(response).__name__}.",
        )
    return dict(response)

class SkillGapIdentifier(BaseAgent):
    """Agent wrapper for skill requirement discovery and gap identification."""

    name: str = "SkillGapIdentifier"

    def __init__(self, model: Any, ) -> None:
        super().__init__(
            model=model,
            system_prompt=skill_gap_identifier_cot_system_prompt,
            task_prompt=skill_gap_identifier_task_prompt_goal2skill,
            jsonalize_output=True,
        )

    def map_goal_to_skill(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Map a learner's goal to the set of required skills."""
        system_prompt = system_prompt or skill_gap_identifier_cot_system_prompt
        task_prompt = task_prompt or skill_gap_identifier_task_prompt_goal2skill
        self.set_prompts(system_prompt, task_prompt)
        raw = self.act(dict(input_dict))
        # Try structured validation; fall back to raw mapping on failure
        try:
            validated = SkillRequirements.model_validate(raw)
            return validated.model_dump()
        except Exception:
            return _ensure_dict(raw, caller=self.__class__.__name__)

    def identify_skill_gap(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Identify knowledge gaps using learner information and expected skills."""

        skill_requirements = input_dict.get("skill_requirements")
        if not isinstance(skill_requirements, Mapping):
            raise ValueError("'skill_requirements' must be supplied as a mapping.")

        system_prompt = system_prompt or skill_gap_identifier_cot_system_prompt
        task_prompt = task_prompt or skill_gap_identifier_task_prompt_identification
        self.set_prompts(system_prompt, task_prompt)
        raw = self.act(dict(input_dict))
        validated = SkillGaps.model_validate(raw)
        return validated.model_dump()

    def reflexion(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Refine an existing goal-to-skill mapping using feedback signals."""

        system_prompt = system_prompt or skill_gap_identifier_cot_system_prompt
        # Fallback: reuse goal2skill prompt for reflexion if a specific one is not defined
        task_prompt = task_prompt or skill_gap_identifier_task_prompt_goal2skill
        self.set_prompts(system_prompt, task_prompt)
        raw = self.act(dict(input_dict))
        validated = SkillRequirements.model_validate(raw)
        return validated.model_dump()


def map_goal_to_skills_with_llm(llm: Any, learning_goal: str) -> JSONDict:
    """Convenience wrapper to map a goal to required skills using the provided LLM."""

    skill_gap_identifier = SkillGapIdentifier(llm)
    return skill_gap_identifier.map_goal_to_skill({"learning_goal": learning_goal})


def identify_skill_gap_with_llm(
    llm: Any,
    learning_goal: str,
    learner_information: str,
    skill_requirements: Optional[Mapping[str, Any]] = None,
    method_name: str = "genmentor",
) -> Tuple[JSONDict, JSONDict]:
    """Identify skill gaps and return both the gaps and the skill requirements used."""

    skill_gap_identifier = SkillGapIdentifier(llm)
    effective_requirements: JSONDict

    if not skill_requirements:
        if method_name == "genmentor":
            effective_requirements = skill_gap_identifier.map_goal_to_skill(
                {"learning_goal": learning_goal},
            )
        elif method_name == "dirgen":
            # For now, reuse the default prompts for dirgen as a fallback
            effective_requirements = skill_gap_identifier.map_goal_to_skill(
                {"learning_goal": learning_goal},
            )
        else:
            raise ValueError("method_name must be either 'genmentor' or 'dirgen'.")
    else:
        effective_requirements = dict(skill_requirements)

    skill_gap = skill_gap_identifier.identify_skill_gap(
        {
            "learning_goal": learning_goal,
            "skill_requirements": effective_requirements,
            "learner_information": learner_information,
        },
    )
    return skill_gap, effective_requirements


def refine_learning_goal_with_llm(
    llm: Any,
    learning_goal: str,
    learner_information: str = "",
) -> JSONDict:
    # Moved to learning_goal_refiner module; re-exported here for backward compatibility
    from .learning_goal_refiner import refine_learning_goal_with_llm as _ref
    return _ref(llm, learning_goal, learner_information)


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