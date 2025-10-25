from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol, Sequence, Union, runtime_checkable

from base import BaseAgent
from .schemas import parse_learning_path_result
from prompts.learning_path_scheduling import (
    learning_path_scheduler_system_prompt,
    learning_path_scheduler_task_prompt_reflexion,
    learning_path_scheduler_task_prompt_reschedule,
    learning_path_scheduler_task_prompt_session,
)


JSONDict = Dict[str, Any]


@runtime_checkable
class SupportsPayload(Protocol):
    """Protocol describing request objects that can be converted into payload dictionaries."""

    def to_payload(self) -> JSONDict:
        """Return a JSON-serialisable dictionary."""
        ...


@dataclass(frozen=True)
class SessionScheduleRequest:
    """Input payload for scheduling sessions."""

    learner_profile: Mapping[str, Any]
    session_count: int = 0

    def to_payload(self) -> JSONDict:
        """Serialize the request into a dictionary understood by the agent."""

        return {
            "learner_profile": dict(self.learner_profile),
            "session_count": self.session_count,
        }


@dataclass(frozen=True)
class LearningPathRefinementRequest:
    """Input payload for reflexion/refinement of a learning path."""

    learning_path: Sequence[Any]
    feedback: Mapping[str, Any]

    def to_payload(self) -> JSONDict:
        """Serialize the request into a dictionary understood by the agent."""

        return {
            "learning_path": list(self.learning_path),
            "feedback": dict(self.feedback),
        }


@dataclass(frozen=True)
class LearningPathRescheduleRequest:
    """Input payload for rescheduling an existing learning path."""

    learner_profile: Mapping[str, Any]
    learning_path: Sequence[Any]
    session_count: Optional[Union[int, str]] = None
    other_feedback: Optional[Union[str, Mapping[str, Any]]] = None

    def to_payload(self) -> JSONDict:
        """Serialize the request into a dictionary understood by the agent."""

        payload: JSONDict = {
            "learner_profile": dict(self.learner_profile),
            "learning_path": list(self.learning_path),
        }
        if self.session_count is not None:
            payload["session_count"] = self.session_count
        if self.other_feedback is not None:
            other = self.other_feedback
            payload["other_feedback"] = (
                dict(other) if isinstance(other, Mapping) else other
            )
        return payload


PayloadInput = Union[SupportsPayload, Mapping[str, Any]]


class LearningPathScheduler(BaseAgent):
    """High-level agent orchestrating learning path scheduling tasks."""
    
    name: str = "LearningPathScheduler"

    def __init__(self, model: Any) -> None:
        """Create a new scheduler bound to a concrete chat model."""

        super().__init__(model=model, system_prompt=learning_path_scheduler_system_prompt, jsonalize_output=True)

    def schedule_session(
            self, 
            input_dict: PayloadInput,
            system_prompt: str = learning_path_scheduler_system_prompt,
            task_prompt: str = learning_path_scheduler_task_prompt_session) -> JSONDict:
        """
        Schedule the learning session based on the provided learner profile, knowledge points, and session count.

        Args:
            input_dict (PayloadInput):
                The learner scheduling payload or request object.
            system_prompt (str):
                The system prompt guiding the LLM.
            task_prompt (str):
                The concrete task prompt for the scheduling action.

        Returns:
            dict: A dictionary containing the scheduled learning sessions based on the provided learner profile, knowledge points, and session count.
        """
        self._ensure_prompts(system_prompt, task_prompt)
        payload = self._coerce_payload(input_dict)
        return self._invoke_agent(payload)

    def reflexion(
        self,
        input_dict: PayloadInput,
        *,
        system_prompt: str = learning_path_scheduler_system_prompt,
        task_prompt: str = learning_path_scheduler_task_prompt_reflexion,
    ) -> JSONDict:
        """
        Refine the learning path based on the provided learning path and evaluator feedback.
        
        Args:
            input_dict (PayloadInput):
                The reflexion payload or request object.

        Returns:
            dict: A dictionary containing the refined learning path based on the provided learning path and evaluator feedback.
        """
        self._ensure_prompts(system_prompt, task_prompt)
        payload = self._coerce_payload(input_dict)
        return self._invoke_agent(payload)

    def reschedule(
        self,
        input_dict: PayloadInput,
        *,
        system_prompt: str = learning_path_scheduler_system_prompt,
        task_prompt: str = learning_path_scheduler_task_prompt_reschedule,
    ) -> JSONDict:
        """
        Reschedule the learning path based on the provided learner profile, learning path, session count, and other feedback.
        
        Args:
            input_dict (PayloadInput):
                The rescheduling payload or request object.

        Returns:
            dict: A dictionary containing the rescheduled learning path based on the provided learner profile, learning path, session count, and other feedback.
        """
        self._ensure_prompts(system_prompt, task_prompt)
        payload = self._coerce_payload(input_dict)
        return self._invoke_agent(payload)

    def _ensure_prompts(self, system_prompt: str, task_prompt: str) -> None:
        """Assign system and task prompts to the underlying agent."""

        self.set_prompts(system_prompt, task_prompt)

    def _coerce_payload(self, payload: PayloadInput) -> JSONDict:
        """Normalise different request flavours into a plain dictionary."""

        if isinstance(payload, SupportsPayload):
            return payload.to_payload()
        return dict(payload)

    def _invoke_agent(self, payload: JSONDict) -> JSONDict:
        """Execute the agent and validate the structured JSON using Pydantic."""

        response = self.act(payload)
        if not isinstance(response, dict):
            raise ValueError(
                "LearningPathScheduler expected a dictionary response but received "
                f"{type(response).__name__}"
            )
        # Validate and normalise output shape: { tracks: [...], result: [sessions...] }
        try:
            validated = parse_learning_path_result(response)
            return validated.model_dump()
        except Exception:
            # Fallback to raw mapping if strict validation fails
            return response

def schedule_learning_path_with_llm(
    llm: Any,
    learner_profile: Mapping[str, Any],
    session_count: int = 0,
    *,
    system_prompt: str = learning_path_scheduler_system_prompt,
    task_prompt: str = learning_path_scheduler_task_prompt_session,
) -> JSONDict:
    """Convenience helper to create a scheduler and produce a new learning path."""

    learning_path_scheduler = LearningPathScheduler(llm)
    request = SessionScheduleRequest(
        learner_profile=learner_profile,
        session_count=session_count,
    )
    return learning_path_scheduler.schedule_session(
        request,
        system_prompt=system_prompt,
        task_prompt=task_prompt,
    )


def reschedule_learning_path_with_llm(
    llm: Any,
    learning_path: Sequence[Any],
    learner_profile: Mapping[str, Any],
    session_count: Optional[int] = None,
    other_feedback: Optional[Union[str, Mapping[str, Any]]] = None,
    *,
    system_prompt: str = learning_path_scheduler_system_prompt,
    task_prompt: str = learning_path_scheduler_task_prompt_reschedule,
) -> JSONDict:
    """Convenience helper to reschedule an existing learning path via the scheduler."""

    learning_path_scheduler = LearningPathScheduler(llm)
    request = LearningPathRescheduleRequest(
        learner_profile=learner_profile,
        learning_path=learning_path,
        session_count=session_count,
        other_feedback=other_feedback,
    )
    return learning_path_scheduler.reschedule(
        request,
        system_prompt=system_prompt,
        task_prompt=task_prompt,
    )


def refine_learning_path_with_llm(
    llm: Any,
    learning_path: Sequence[Any],
    feedback: Mapping[str, Any],
    *,
    system_prompt: str = learning_path_scheduler_system_prompt,
    task_prompt: str = learning_path_scheduler_task_prompt_reflexion,
) -> JSONDict:
    """Convenience helper around :meth:`LearningPathScheduler.reflexion`."""

    learning_path_scheduler = LearningPathScheduler(llm)
    request = LearningPathRefinementRequest(
        learning_path=learning_path,
        feedback=feedback,
    )
    return learning_path_scheduler.reflexion(
        request,
        system_prompt=system_prompt,
        task_prompt=task_prompt,
    )


__all__ = [
    "LearningPathScheduler",
    "LearningPathRefinementRequest",
    "LearningPathRescheduleRequest",
    "SessionScheduleRequest",
    "schedule_learning_path_with_llm",
    "refine_learning_path_with_llm",
    "reschedule_learning_path_with_llm",
]