from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Union, cast

from base.agent import Agent
from prompts import automated_evaluation as automated_prompts

EvaluationResult = dict[str, Any]
EvaluationOutput = Union[EvaluationResult, list[EvaluationResult]]
BatchItems = Sequence[Mapping[str, Any]]


def _select_prompt(*, batch_mode: bool, single_prompt: str, batch_prompt: str) -> str:
    """Return the appropriate task prompt depending on ``batch_mode``."""

    return batch_prompt if batch_mode else single_prompt


def _collect_batch_ids(items: BatchItems) -> list[Any]:
    """Extract the ``id`` field from each batch item, validating presence."""

    batch_ids: list[Any] = []
    for item in items:
        if "id" not in item:
            raise KeyError("Each batch entry must include an 'id' field.")
        batch_ids.append(item["id"])
    return batch_ids


def _materialize_items(items: BatchItems) -> list[dict[str, Any]]:
    """Create shallow copies of batch input mappings for serialization."""

    return [dict(item) for item in items]


def _normalize_result(result: EvaluationOutput) -> list[EvaluationResult]:
    """Normalize the agent output to a list of evaluation dictionaries."""

    if isinstance(result, Mapping):
        return [dict(result)]

    if isinstance(result, Sequence) and not isinstance(result, (str, bytes, bytearray)):
        normalized: list[EvaluationResult] = []
        for entry in result:
            if not isinstance(entry, Mapping):
                raise TypeError("LLM batch outputs must be mappings.")
            normalized.append(dict(entry))
        return normalized

    raise TypeError("LLM output must be either a mapping or a sequence of mappings.")


def _ensure_single_result(result: EvaluationOutput) -> EvaluationResult:
    """Return a single evaluation mapping from the agent output."""

    if isinstance(result, Mapping):
        return dict(result)

    if isinstance(result, Sequence) and not isinstance(result, (str, bytes, bytearray)):
        if not result:
            raise ValueError("LLM returned an empty sequence for a single evaluation.")
        first_entry = result[0]
        if not isinstance(first_entry, Mapping):
            raise TypeError("Each LLM output entry must be a mapping.")
        return dict(first_entry)

    raise TypeError("LLM output must be a mapping when batch_mode is False.")


class BaseEvaluationAgent(Agent):
    """Shared utilities for automated evaluation agents."""

    def __init__(self, name: str, llm: Any, system_prompt: str) -> None:
        super().__init__(name, llm=llm, json_output=True)
        self._system_prompt = system_prompt

    def _evaluate(
        self,
        payload: Mapping[str, Any],
        *,
        task_prompt: str,
        batch_mode: bool = False,
    ) -> EvaluationOutput:
        """Execute the evaluation with the configured prompts."""

        self.set_prompts(self._system_prompt, task_prompt)
        return cast(EvaluationOutput, self.act(dict(payload), batch_mode=batch_mode))


class Goal2SkillMappingEvaluator(BaseEvaluationAgent):
    """LLM-backed evaluator for goal-to-skill mapping quality."""

    def __init__(self, llm: Any) -> None:
        super().__init__(
            "Goal2SkillMappingEvaluator",
            llm,
            automated_prompts.goal2skill_mapping_evaluator_system_prompt,
        )

    def evaluate_goal2skill_mapping(
        self,
        input_payload: Mapping[str, Any],
        *,
        eval_type: Literal["validation", "scoring"] = "validation",
        batch_mode: bool = False,
    ) -> EvaluationOutput:
        """Evaluate goal-to-skill mappings for validation or scoring purposes."""

        prompt_mapping: dict[str, tuple[str, str]] = {
            "validation": (
                automated_prompts.goal2skill_mapping_evaluator_task_prompt_validation,
                automated_prompts.goal2skill_mapping_evaluator_task_prompt_batch_validation,
            ),
            "scoring": (
                automated_prompts.goal2skill_mapping_evaluator_task_prompt_scoring,
                automated_prompts.goal2skill_mapping_evaluator_task_prompt_batch_scoring,
            ),
        }

        if eval_type not in prompt_mapping:
            raise ValueError(f"Invalid evaluation type: {eval_type}")

        single_prompt, batch_prompt = prompt_mapping[eval_type]
        task_prompt = _select_prompt(
            batch_mode=batch_mode,
            single_prompt=single_prompt,
            batch_prompt=batch_prompt,
        )
        return self._evaluate(input_payload, task_prompt=task_prompt, batch_mode=batch_mode)


class SkillGapEvaluator(BaseEvaluationAgent):
    """LLM-backed evaluator for learner skill gaps."""

    def __init__(self, llm: Any) -> None:
        super().__init__(
            "SkillGapEvaluator",
            llm,
            automated_prompts.skill_gap_evaluator_system_prompt,
        )

    def evaluate_skill_gap(
        self,
        input_payload: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> EvaluationOutput:
        """Evaluate skill gaps for a learner profile."""

        task_prompt = _select_prompt(
            batch_mode=batch_mode,
            single_prompt=automated_prompts.skill_gap_evaluator_task_prompt,
            batch_prompt=automated_prompts.skill_gap_evaluator_task_prompt_batch,
        )
        return self._evaluate(input_payload, task_prompt=task_prompt, batch_mode=batch_mode)


class LearningPathEvaluator(BaseEvaluationAgent):
    """LLM-backed evaluator for generated learning paths."""

    def __init__(self, llm: Any) -> None:
        super().__init__(
            "LearningPathEvaluator",
            llm,
            automated_prompts.learning_path_evaluator_system_prompt,
        )

    def evaluate_learning_path(
        self,
        input_payload: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> EvaluationOutput:
        """Evaluate recommended learning paths for a learner."""

        task_prompt = _select_prompt(
            batch_mode=batch_mode,
            single_prompt=automated_prompts.learning_path_evaluator_task_prompt,
            batch_prompt=automated_prompts.learning_path_evaluator_task_prompt_batch,
        )
        return self._evaluate(input_payload, task_prompt=task_prompt, batch_mode=batch_mode)


class LearnerProfileEvaluator(BaseEvaluationAgent):
    """LLM-backed evaluator for learner profiles."""

    def __init__(self, llm: Any) -> None:
        super().__init__(
            "LearnerProfileEvaluator",
            llm,
            automated_prompts.learner_profile_evaluator_system_prompt,
        )

    def evaluate_learner_profile(
        self,
        input_payload: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> EvaluationOutput:
        """Evaluate learner profile quality and completeness."""

        task_prompt = _select_prompt(
            batch_mode=batch_mode,
            single_prompt=automated_prompts.learner_profile_evaluator_task_prompt,
            batch_prompt=automated_prompts.learner_profile_evaluator_task_prompt_batch,
        )
        return self._evaluate(input_payload, task_prompt=task_prompt, batch_mode=batch_mode)


class LearningContentEvaluator(BaseEvaluationAgent):
    """LLM-backed evaluator for learning content recommendations."""

    def __init__(self, llm: Any) -> None:
        super().__init__(
            "LearningContentEvaluator",
            llm,
            automated_prompts.learning_content_evaluator_system_prompt,
        )

    def evaluate_learning_content(
        self,
        input_payload: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> EvaluationOutput:
        """Evaluate curated learning content for relevance and coverage."""

        task_prompt = _select_prompt(
            batch_mode=batch_mode,
            single_prompt=automated_prompts.learning_content_evaluator_task_prompt,
            batch_prompt=automated_prompts.learning_content_evaluator_task_prompt_batch,
        )
        return self._evaluate(input_payload, task_prompt=task_prompt, batch_mode=batch_mode)


def evaluate_batch_goal2skill_mapping_with_llm(
    llm: Any,
    learning_goal: str,
    skills_in_validation: Sequence[str],
    batch_skill_requirements: BatchItems,
    *,
    batch_eval: bool = False,
    eval_type: Literal["validation", "scoring"] = "validation",
) -> list[EvaluationResult]:
    """Evaluate goal-to-skill mappings for a batch of candidate methods."""

    evaluator = Goal2SkillMappingEvaluator(llm)

    if batch_eval:
        payload = {
            "learning_goal": learning_goal,
            "skills_in_validation": list(skills_in_validation),
            "batch_ids": _collect_batch_ids(batch_skill_requirements),
            "batch_skill_requirements": _materialize_items(batch_skill_requirements),
        }
        result = evaluator.evaluate_goal2skill_mapping(
            payload,
            eval_type=eval_type,
            batch_mode=True,
        )
        return _normalize_result(result)

    evaluations: list[EvaluationResult] = []
    for skill_requirement in batch_skill_requirements:
        if "id" not in skill_requirement:
            raise KeyError("Each skill requirement must include an 'id' field.")

        payload = {
            "learning_goal": learning_goal,
            "skills_in_validation": list(skills_in_validation),
            "skill_requirements": dict(skill_requirement),
        }
        result = evaluator.evaluate_goal2skill_mapping(
            payload,
            eval_type=eval_type,
            batch_mode=False,
        )
        evaluation = _ensure_single_result(result)
        evaluation["id"] = skill_requirement["id"]
        evaluations.append(evaluation)

    return evaluations


def evaluate_batch_skill_gap_with_llm(
    llm: Any,
    learning_goal: str,
    learner_information: Mapping[str, Any],
    batch_skill_gaps: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[EvaluationResult]:
    """Evaluate learner skill gaps for single or batched inputs."""

    evaluator = SkillGapEvaluator(llm)
    base_payload = {
        "learning_goal": learning_goal,
        "learner_information": dict(learner_information),
    }

    if batch_eval:
        payload = {
            **base_payload,
            "batch_ids": _collect_batch_ids(batch_skill_gaps),
            "batch_skill_gaps": _materialize_items(batch_skill_gaps),
        }
        result = evaluator.evaluate_skill_gap(payload, batch_mode=True)
        return _normalize_result(result)

    evaluations: list[EvaluationResult] = []
    for skill_gap in batch_skill_gaps:
        if "id" not in skill_gap:
            raise KeyError("Each skill gap must include an 'id' field.")

        payload = {
            **base_payload,
            "skill_gap": dict(skill_gap),
        }
        result = evaluator.evaluate_skill_gap(payload, batch_mode=False)
        evaluation = _ensure_single_result(result)
        evaluation["id"] = skill_gap["id"]
        evaluations.append(evaluation)

    return evaluations


def evaluate_batch_learning_path_with_llm(
    llm: Any,
    learner_profile: Mapping[str, Any],
    batch_learning_paths: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[EvaluationResult]:
    """Evaluate learning paths produced for a learner profile."""

    evaluator = LearningPathEvaluator(llm)
    base_payload = {"learner_profile": dict(learner_profile)}

    if batch_eval:
        payload = {
            **base_payload,
            "batch_ids": _collect_batch_ids(batch_learning_paths),
            "batch_learning_paths": _materialize_items(batch_learning_paths),
        }
        result = evaluator.evaluate_learning_path(payload, batch_mode=True)
        return _normalize_result(result)

    evaluations: list[EvaluationResult] = []
    for learning_path in batch_learning_paths:
        if "id" not in learning_path:
            raise KeyError("Each learning path must include an 'id' field.")

        payload = {
            **base_payload,
            "learning_path": dict(learning_path),
        }
        result = evaluator.evaluate_learning_path(payload, batch_mode=False)
        evaluation = _ensure_single_result(result)
        evaluation["id"] = learning_path["id"]
        evaluations.append(evaluation)

    return evaluations


def evaluate_batch_learner_profile_with_llm(
    llm: Any,
    batch_learner_profiles: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[EvaluationResult]:
    """Evaluate learner profiles for quality and completeness."""

    evaluator = LearnerProfileEvaluator(llm)

    if batch_eval:
        payload = {
            "batch_ids": _collect_batch_ids(batch_learner_profiles),
            "batch_learner_profiles": _materialize_items(batch_learner_profiles),
        }
        result = evaluator.evaluate_learner_profile(payload, batch_mode=True)
        return _normalize_result(result)

    evaluations: list[EvaluationResult] = []
    for learner_profile in batch_learner_profiles:
        if "id" not in learner_profile:
            raise KeyError("Each learner profile must include an 'id' field.")

        payload = {"learner_profile": dict(learner_profile)}
        result = evaluator.evaluate_learner_profile(payload, batch_mode=False)
        evaluation = _ensure_single_result(result)
        evaluation["id"] = learner_profile["id"]
        evaluations.append(evaluation)

    return evaluations


def evaluate_batch_learning_content_with_llm(
    llm: Any,
    learner_profile: Mapping[str, Any],
    batch_learning_content: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[EvaluationResult]:
    """Evaluate learning content recommendations for a learner profile."""

    evaluator = LearningContentEvaluator(llm)
    base_payload = {"learner_profile": dict(learner_profile)}

    if batch_eval:
        payload = {
            **base_payload,
            "batch_ids": _collect_batch_ids(batch_learning_content),
            "batch_learning_content": _materialize_items(batch_learning_content),
        }
        result = evaluator.evaluate_learning_content(payload, batch_mode=True)
        return _normalize_result(result)

    evaluations: list[EvaluationResult] = []
    for learning_content in batch_learning_content:
        if "id" not in learning_content:
            raise KeyError("Each learning content item must include an 'id' field.")

        payload = {
            **base_payload,
            "learning_content": dict(learning_content),
        }
        result = evaluator.evaluate_learning_content(payload, batch_mode=False)
        evaluation = _ensure_single_result(result)
        evaluation["id"] = learning_content["id"]
        evaluations.append(evaluation)

    return evaluations
