from __future__ import annotations

from typing import Any, Callable, Mapping, MutableMapping, Sequence, Literal

from base.agent import Agent
from prompts.automated_scoring import (
    goal2skill_mapping_scorer_system_prompt,
    goal2skill_mapping_scorer_task_prompt_batch_scoring,
    goal2skill_mapping_scorer_task_prompt_batch_validation,
    goal2skill_mapping_scorer_task_prompt_scoring,
    goal2skill_mapping_scorer_task_prompt_validation,
    learner_profile_scorer_system_prompt,
    learner_profile_scorer_task_prompt,
    learner_profile_scorer_task_prompt_batch,
    learning_content_scorer_system_prompt,
    learning_content_scorer_task_prompt,
    learning_content_scorer_task_prompt_batch,
    learning_path_scorer_system_prompt,
    learning_path_scorer_task_prompt,
    learning_path_scorer_task_prompt_batch,
    skill_gap_scorer_system_prompt,
    skill_gap_scorer_task_prompt,
    skill_gap_scorer_task_prompt_batch,
)

JsonDict = dict[str, Any]
BatchItem = Mapping[str, Any]
BatchItems = Sequence[BatchItem]
ScoreCallable = Callable[[JsonDict, bool], Any]
BatchPayloadBuilder = Callable[[BatchItems], JsonDict]
SinglePayloadBuilder = Callable[[BatchItem], JsonDict]


def _ensure_dict(result: Any) -> JsonDict:
    """Return a shallow ``dict`` copy from any mapping result."""

    if isinstance(result, MutableMapping):
        return dict(result)
    if isinstance(result, Mapping):
        return dict(result)
    raise TypeError(f"Expected mapping result, received {type(result).__name__}.")


def _ensure_sequence_of_dicts(result: Any) -> list[JsonDict]:
    """Normalize scorer responses into a list of dictionaries."""

    if isinstance(result, Mapping):
        return [dict(result)]
    if isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
        return [
            dict(item) if isinstance(item, Mapping) else _ensure_dict(item)
            for item in result
        ]
    raise TypeError(
        "Expected a mapping or sequence of mappings from scorer response, "
        f"received {type(result).__name__}."
    )


def _extract_ids(items: BatchItems, *, id_field: str = "id") -> list[Any]:
    """Pull the identifier column from each batch item."""

    return [item[id_field] for item in items]


def _execute_scoring_workflow(
    score_callable: ScoreCallable,
    *,
    items: BatchItems,
    batch_eval: bool,
    batch_payload_builder: BatchPayloadBuilder,
    single_payload_builder: SinglePayloadBuilder,
    id_field: str = "id",
) -> list[JsonDict]:
    """Execute individual or batch scoring with consistent post-processing."""

    materialized_items = list(items)
    if batch_eval:
        batch_payload = batch_payload_builder(materialized_items)
        batch_result = score_callable(batch_payload, True)
        return _ensure_sequence_of_dicts(batch_result)

    evaluations: list[JsonDict] = []
    for item in materialized_items:
        payload = single_payload_builder(item)
        single_result = score_callable(payload, False)
        normalized_result = _ensure_dict(single_result)
        if id_field in item:
            normalized_result.setdefault(id_field, item[id_field])
        evaluations.append(normalized_result)
    return evaluations


class Goal2SkillMappingScorer(Agent):
    """Agent orchestrating goal-to-skill mapping validations and scorings."""

    def __init__(self, llm: Any) -> None:
        """Initialize the scorer with the provided LLM backend."""

        super().__init__("Goal2SkillMappingScorer", llm=llm, json_output=True)

    def score_goal2skill_mapping(
        self,
        input_dict: Mapping[str, Any],
        *,
        batch_mode: bool = False,
        eval_type: Literal["validation", "scoring"] = "validation",
    ) -> Any:
        """Run the goal-to-skill mapping evaluation with the correct prompt."""

        if eval_type == "validation":
            task_prompt = (
                goal2skill_mapping_scorer_task_prompt_batch_validation
                if batch_mode
                else goal2skill_mapping_scorer_task_prompt_validation
            )
        else:
            task_prompt = (
                goal2skill_mapping_scorer_task_prompt_batch_scoring
                if batch_mode
                else goal2skill_mapping_scorer_task_prompt_scoring
            )

        self.set_prompts(goal2skill_mapping_scorer_system_prompt, task_prompt)
        return self.act(dict(input_dict), batch_mode=batch_mode)


class LearnerProfileScorer(Agent):
    """Agent responsible for evaluating learner profile accuracy."""

    def __init__(self, llm: Any) -> None:
        """Initialize the learner profile scorer."""

        super().__init__("LearnerProfileScorer", llm=llm, json_output=True)

    def score_learner_profile(
        self,
        input_dict: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> Any:
        """Evaluate learner profiles against provided references."""

        task_prompt = (
            learner_profile_scorer_task_prompt_batch
            if batch_mode
            else learner_profile_scorer_task_prompt
        )
        self.set_prompts(learner_profile_scorer_system_prompt, task_prompt)
        return self.act(dict(input_dict), batch_mode=batch_mode)


class SkillGapScorer(Agent):
    """Agent evaluating skill gaps for a learner goal."""

    def __init__(self, llm: Any) -> None:
        """Initialize the skill gap scorer."""

        super().__init__("SkillGapScorer", llm=llm, json_output=True)

    def score_skill_gap(
        self,
        input_dict: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> Any:
        """Score skill gaps using the dedicated prompts."""

        task_prompt = (
            skill_gap_scorer_task_prompt_batch
            if batch_mode
            else skill_gap_scorer_task_prompt
        )
        self.set_prompts(skill_gap_scorer_system_prompt, task_prompt)
        return self.act(dict(input_dict), batch_mode=batch_mode)


class LearningPathScorer(Agent):
    """Agent evaluating learning paths across multiple dimensions."""

    def __init__(self, llm: Any) -> None:
        """Initialize the learning path scorer."""

        super().__init__("LearningPathScorer", llm=llm, json_output=True)

    def score_learning_path(
        self,
        input_dict: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> Any:
        """Score learning paths by configuring the appropriate prompts."""

        task_prompt = (
            learning_path_scorer_task_prompt_batch
            if batch_mode
            else learning_path_scorer_task_prompt
        )
        self.set_prompts(learning_path_scorer_system_prompt, task_prompt)
        return self.act(dict(input_dict), batch_mode=batch_mode)


class LearningContentScorer(Agent):
    """Agent reviewing learning content quality and alignment."""

    def __init__(self, llm: Any) -> None:
        """Initialize the learning content scorer."""

        super().__init__("LearningContentScorer", llm=llm, json_output=True)

    def score_learning_content(
        self,
        input_dict: Mapping[str, Any],
        *,
        batch_mode: bool = False,
    ) -> Any:
        """Assess learning content with the configured prompt."""

        task_prompt = (
            learning_content_scorer_task_prompt_batch
            if batch_mode
            else learning_content_scorer_task_prompt
        )
        self.set_prompts(learning_content_scorer_system_prompt, task_prompt)
        return self.act(dict(input_dict), batch_mode=batch_mode)


def score_batch_goal2skill_mapping_with_llm(
    llm: Any,
    learning_goal: str,
    skills_in_validation: Sequence[str] | None,
    batch_skill_requirements: BatchItems,
    *,
    batch_eval: bool = False,
    eval_type: Literal["validation", "scoring"] = "validation",
) -> list[JsonDict]:
    """Evaluate identified skill requirements for a goal using an LLM scorer."""

    if eval_type == "validation" and skills_in_validation is None:
        raise ValueError("'skills_in_validation' must be provided when eval_type='validation'.")

    scorer = Goal2SkillMappingScorer(llm)
    materialized_requirements = list(batch_skill_requirements)
    validation_skills = list(skills_in_validation) if skills_in_validation is not None else None

    def build_batch_payload(items: BatchItems) -> JsonDict:
        """Assemble the batched payload sent to the scorer."""

        return {
            "learning_goal": learning_goal,
            "skills_in_validation": validation_skills,
            "batch_ids": _extract_ids(items),
            "batch_skill_requirements": list(items),
        }

    def build_single_payload(item: BatchItem) -> JsonDict:
        """Build the payload for scoring a single skill requirement entry."""

        payload: JsonDict = {
            "learning_goal": learning_goal,
            "skill_requirements": item,
        }
        if validation_skills is not None:
            payload["skills_in_validation"] = validation_skills
        return payload

    def call(payload: JsonDict, use_batch: bool) -> Any:
        """Invoke the scorer with the prepared payload."""

        cleaned_payload = {
            key: value
            for key, value in payload.items()
            if value is not None
        }
        return scorer.score_goal2skill_mapping(
            cleaned_payload,
            batch_mode=use_batch,
            eval_type=eval_type,
        )

    return _execute_scoring_workflow(
        call,
        items=materialized_requirements,
        batch_eval=batch_eval,
        batch_payload_builder=build_batch_payload,
        single_payload_builder=build_single_payload,
    )


def score_batch_skill_gap_with_llm(
    llm: Any,
    learning_goal: str,
    learner_information: Mapping[str, Any],
    batch_skill_gaps: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[JsonDict]:
    """Evaluate detected skill gaps for a learner goal."""

    scorer = SkillGapScorer(llm)
    learner_info_payload = dict(learner_information)

    def build_batch_payload(items: BatchItems) -> JsonDict:
        """Create the payload for batched skill gap evaluation."""

        return {
            "learning_goal": learning_goal,
            "learner_information": learner_info_payload,
            "batch_ids": _extract_ids(items),
            "batch_skill_gaps": list(items),
        }

    def build_single_payload(item: BatchItem) -> JsonDict:
        """Create the payload for evaluating a single skill gap."""

        return {
            "learning_goal": learning_goal,
            "learner_information": learner_info_payload,
            "skill_gap": item,
        }

    return _execute_scoring_workflow(
        scorer.score_skill_gap,
        items=batch_skill_gaps,
        batch_eval=batch_eval,
        batch_payload_builder=build_batch_payload,
        single_payload_builder=build_single_payload,
    )


def score_batch_learning_path_with_llm(
    llm: Any,
    learner_profile: Mapping[str, Any],
    batch_learning_paths: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[JsonDict]:
    """Score multiple learning paths against a learner profile."""

    scorer = LearningPathScorer(llm)
    learner_profile_payload = dict(learner_profile)

    def build_batch_payload(items: BatchItems) -> JsonDict:
        """Create the payload for batched learning path scoring."""

        return {
            "learner_profile": learner_profile_payload,
            "batch_ids": _extract_ids(items),
            "batch_learning_paths": list(items),
        }

    def build_single_payload(item: BatchItem) -> JsonDict:
        """Create the payload for scoring a single learning path."""

        return {
            "learner_profile": learner_profile_payload,
            "learning_path": item,
        }

    return _execute_scoring_workflow(
        scorer.score_learning_path,
        items=batch_learning_paths,
        batch_eval=batch_eval,
        batch_payload_builder=build_batch_payload,
        single_payload_builder=build_single_payload,
    )


def score_batch_learner_profile_with_llm(
    llm: Any,
    batch_learner_profiles: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[JsonDict]:
    """Evaluate generated learner profiles against a ground-truth reference."""

    scorer = LearnerProfileScorer(llm)

    def build_batch_payload(items: BatchItems) -> JsonDict:
        """Create the payload for batched learner profile scoring."""

        return {
            "batch_ids": _extract_ids(items),
            "batch_learner_profiles": list(items),
        }

    def build_single_payload(item: BatchItem) -> JsonDict:
        """Create the payload for scoring a single learner profile."""

        return {"learner_profile": item}

    return _execute_scoring_workflow(
        scorer.score_learner_profile,
        items=batch_learner_profiles,
        batch_eval=batch_eval,
        batch_payload_builder=build_batch_payload,
        single_payload_builder=build_single_payload,
    )


def score_batch_learning_content_with_llm(
    llm: Any,
    learner_profile: Mapping[str, Any],
    batch_learning_content: BatchItems,
    *,
    batch_eval: bool = False,
) -> list[JsonDict]:
    """Assess learning content choices for a given learner profile."""

    scorer = LearningContentScorer(llm)
    learner_profile_payload = dict(learner_profile)

    def build_batch_payload(items: BatchItems) -> JsonDict:
        """Create the payload for batched learning content scoring."""

        return {
            "learner_profile": learner_profile_payload,
            "batch_ids": _extract_ids(items),
            "batch_learning_content": list(items),
        }

    def build_single_payload(item: BatchItem) -> JsonDict:
        """Create the payload for scoring a single learning content item."""

        return {
            "learner_profile": learner_profile_payload,
            "learning_content": item,
        }

    return _execute_scoring_workflow(
        scorer.score_learning_content,
        items=batch_learning_content,
        batch_eval=batch_eval,
        batch_payload_builder=build_batch_payload,
        single_payload_builder=build_single_payload,
    )