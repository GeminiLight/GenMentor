from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, Optional, TypeAlias

from base import BaseAgent
from .prompts import (
	learning_goal_refiner_system_prompt,
	learning_goal_refiner_task_prompt,
)
from .schemas import RefinedLearningGoal

JSONDict: TypeAlias = Dict[str, Any]


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
		raw = self.act(dict(input_dict))
		validated = RefinedLearningGoal.model_validate(raw)
		return validated.model_dump()

def refine_learning_goal_with_llm(
	llm: Any,
	learning_goal: str,
	learner_information: str = "",
) -> JSONDict:
	"""Refine a learner's goal using the provided LLM."""

	refiner = LearningGoalRefiner(llm)
	return refiner.refine_goal(
		{
			"learning_goal": learning_goal,
			"learner_information": learner_information,
		},
	)

