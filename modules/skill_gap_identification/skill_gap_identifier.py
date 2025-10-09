from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple, TypeAlias

from base import Agent
from prompts.skill_gap_identification import (
    learning_goal_refiner_system_prompt,
    learning_goal_refiner_task_prompt,
    skill_gap_identifier_cot_system_prompt,
    skill_gap_identifier_dirgen_system_prompt,
    skill_gap_identifier_task_prompt_goal2skill,
    skill_gap_identifier_task_prompt_goal2skill_reflexion,
    skill_gap_identifier_task_prompt_identification,
)

JSONDict: TypeAlias = Dict[str, Any]


def _validate_key(input_dict: Mapping[str, Any], key: str) -> None:
    """Ensure that the expected key exists and contains a non-empty string."""

    value = input_dict.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{key}' must be provided as a non-empty string.")


def _ensure_dict(response: Any, *, caller: str) -> JSONDict:
    """Guarantee that the LLM response is JSON-like."""

    if not isinstance(response, Mapping):
        raise TypeError(
            f"{caller} expected a mapping response, received {type(response).__name__}.",
        )
    return dict(response)


class SkillGapIdentifier(Agent):
    """Agent wrapper for skill requirement discovery and gap identification."""

    def __init__(self, llm: Any) -> None:
        super().__init__(name="SkillGapIdentifier", llm=llm, json_output=True)

    def map_goal_to_skill(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Map a learner's goal to the set of required skills."""

        _validate_key(input_dict, "learning_goal")
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

        _validate_key(input_dict, "learning_goal")
        _validate_key(input_dict, "learner_information")

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

        _validate_key(input_dict, "learning_goal")
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


class LearningGoalRefiner(Agent):
    """Agent wrapper for refining learner goals."""

    def __init__(self, llm: Any) -> None:
        super().__init__(name="LearningGoalRefiner", llm=llm, json_output=True)

    def refine_goal(
        self,
        input_dict: Mapping[str, Any],
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
    ) -> JSONDict:
        """Refine a learner's goal using contextual learner information."""

        _validate_key(input_dict, "learning_goal")
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