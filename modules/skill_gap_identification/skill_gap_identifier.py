from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple, TypeAlias
from langchain.agents.structured_output import ToolStrategy

from base import BaseAgent
from modules.skill_gap_identification.prompts import (
    learning_goal_refiner_system_prompt,
    learning_goal_refiner_task_prompt,
    skill_gap_identifier_cot_system_prompt,
    skill_gap_identifier_task_prompt_goal2skill,
    skill_gap_identifier_task_prompt_identification,
)

JSONDict: TypeAlias = Dict[str, Any]



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
        return self._run_with_prompts(input_dict, system_prompt, task_prompt)

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
        return self._run_with_prompts(input_dict, system_prompt, task_prompt)

    def reflexion(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Refine an existing goal-to-skill mapping using feedback signals."""

        system_prompt = system_prompt or skill_gap_identifier_cot_system_prompt
        task_prompt = task_prompt or skill_gap_identifier_task_prompt_goal2skill_reflexion
        return self._run_with_prompts(input_dict, system_prompt, task_prompt)

    def _run_with_prompts(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: str,
        task_prompt: str,
    ) -> JSONDict:
        """Set prompts and execute the agent safely."""

        self.set_prompts(system_prompt, task_prompt)
        response = self.act(dict(input_dict))
        return _ensure_dict(response, caller=self.__class__.__name__)


class LearningGoalRefiner(BaseAgent):
    """Agent wrapper for refining learner goals."""

    name: str = "LearningGoalRefiner"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, system_prompt=learning_goal_refiner_system_prompt, jsonalize_output=True)

    def refine_goal(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Refine a learner's goal using contextual learner information."""

        system_prompt = system_prompt or learning_goal_refiner_system_prompt
        task_prompt = task_prompt or learning_goal_refiner_task_prompt
        self.set_prompts(system_prompt, task_prompt)
        response = self.act(dict(input_dict))
        return _ensure_dict(response, caller=self.__class__.__name__)


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
            effective_requirements = skill_gap_identifier.map_goal_to_skill(
                {"learning_goal": learning_goal},
                system_prompt=skill_gap_identifier_dirgen_system_prompt,
                task_prompt=skill_gap_identifier_task_prompt_goal2skill,
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
    """Refine a learner's goal using the provided LLM."""

    learning_goal_refiner = LearningGoalRefiner(llm)
    return learning_goal_refiner.refine_goal(
        {
            "learning_goal": learning_goal,
            "learner_information": learner_information,
        },
    )


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