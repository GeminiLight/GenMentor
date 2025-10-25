"""Utilities for building and updating adaptive learner profiles via LLMs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Union, Protocol, runtime_checkable

from base import BaseAgent
from .schemas import parse_learner_profile_result
from prompts import (
    adaptive_learner_profiler_system_prompt,
    adaptive_learner_profiler_task_prompt_initialization,
    adaptive_learner_profiler_task_prompt_update,
)


logger = logging.getLogger(__name__)


class AdaptiveLearnerProfilerError(RuntimeError):
    """Domain-specific error raised when profiling requests fail."""


@dataclass(slots=True)
class LearnerProfileInitializationPayload:
    """Typed container for the inputs needed to bootstrap a learner profile."""

    learning_goal: str
    learner_information: Mapping[str, Any]
    skill_gap: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation expected by the agent."""

        return {
            "learning_goal": self.learning_goal,
            "learner_information": self.learner_information,
            "skill_gap": self.skill_gap,
        }


@dataclass(slots=True)
class LearnerProfileUpdatePayload:
    """Typed container for the inputs used to refine an existing learner profile."""

    learner_profile: Mapping[str, Any]
    learner_interactions: Union[str, Mapping[str, Any]]
    learner_information: Mapping[str, Any]
    session_information: Optional[Union[str, Mapping[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation expected by the agent."""

        payload: Dict[str, Any] = {
            "learner_profile": self.learner_profile,
            "learner_interactions": self.learner_interactions,
            "learner_information": self.learner_information,
        }
        if self.session_information not in (None, ""):
            payload["session_information"] = self.session_information
        return payload


InitializationPayloadLike = Union[Mapping[str, Any], LearnerProfileInitializationPayload]
UpdatePayloadLike = Union[Mapping[str, Any], LearnerProfileUpdatePayload]


@runtime_checkable
class SupportsToDict(Protocol):
    def to_dict(self) -> Dict[str, Any]:
        ...


PayloadLike = Union[Mapping[str, Any], SupportsToDict]


def _payload_to_dict(payload: PayloadLike) -> Dict[str, Any]:
    """Coerce supported payload types into the dictionary format expected by the agent."""

    if isinstance(payload, Mapping):
        return dict(payload)
    # Any object conforming to SupportsToDict (e.g., our dataclasses) works here
    if isinstance(payload, SupportsToDict):
        return payload.to_dict()
    raise TypeError(f"Unsupported payload type: {type(payload)!r}")


class AdaptiveLearnerProfiler(BaseAgent):
    """Agent wrapper that coordinates the prompts required for learner profiling."""

    name: str = "AdaptiveLearnerProfiler"

    def __init__(self, llm: Any) -> None:
        """Create a profiler that leverages a large language model backend."""

        super().__init__(
            model=llm,
            jsonalize_output=True,
        )

    def initialize_profile(self, input_payload: InitializationPayloadLike) -> Dict[str, Any]:
        """Generate an initial learner profile using the provided onboarding information."""

        payload = _payload_to_dict(input_payload)
        self.set_prompts(
            adaptive_learner_profiler_system_prompt,
            adaptive_learner_profiler_task_prompt_initialization,
        )
        return self._execute(payload, action="initialize")

    def update_profile(self, input_payload: UpdatePayloadLike) -> Dict[str, Any]:
        """Update an existing learner profile with fresh interaction data."""

        payload = _payload_to_dict(input_payload)
        self.set_prompts(
            adaptive_learner_profiler_system_prompt,
            adaptive_learner_profiler_task_prompt_update,
        )
        return self._execute(payload, action="update")

    def _execute(self, payload: Dict[str, Any], *, action: str) -> Dict[str, Any]:
        """Execute the agent call while providing consistent error handling and validation."""

        try:
            raw = self.act(payload)
            # Validate and normalize via Pydantic; fall back to raw mapping
            if isinstance(raw, dict):
                try:
                    validated = parse_learner_profile_result(raw)
                    return validated.model_dump()
                except Exception:
                    return raw
            return raw
        except Exception as exc:  # noqa: BLE001 - bubble up domain-specific error
            logger.exception("Failed to %s learner profile", action)
            raise AdaptiveLearnerProfilerError(
                f"Unable to {action} learner profile with the provided payload."
            ) from exc

def initialize_learner_profile_with_llm(
    llm: Any,
    learning_goal: str,
    learner_information: Mapping[str, Any],
    skill_gap: Mapping[str, Any],
    method_name: str = "genmentor",
) -> Dict[str, Any]:
    """Public helper for generating a learner profile with minimal boilerplate."""

    logger.debug("Initializing learner profile using method '%s'", method_name)
    learner_profiler = AdaptiveLearnerProfiler(llm)
    payload = LearnerProfileInitializationPayload(
        learning_goal=learning_goal,
        learner_information=learner_information,
        skill_gap=skill_gap,
    )
    try:
        return learner_profiler.initialize_profile(payload)
    except AdaptiveLearnerProfilerError:
        raise
    except Exception as exc:  # noqa: BLE001 - convert to domain error
        raise AdaptiveLearnerProfilerError("LLM-backed learner profiling failed.") from exc


def update_learner_profile_with_llm(
    llm: Any,
    learner_profile: Mapping[str, Any],
    learner_interactions: Union[str, Mapping[str, Any]],
    learner_information: Mapping[str, Any],
    session_information: Optional[Union[str, Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Public helper for updating an existing learner profile via the LLM backend."""

    learner_profiler = AdaptiveLearnerProfiler(llm)
    payload = LearnerProfileUpdatePayload(
        learner_profile=learner_profile,
        learner_interactions=learner_interactions,
        learner_information=learner_information,
        session_information=session_information,
    )
    try:
        return learner_profiler.update_profile(payload)
    except AdaptiveLearnerProfilerError:
        raise
    except Exception as exc:  # noqa: BLE001 - convert to domain error
        raise AdaptiveLearnerProfilerError("LLM-backed learner profile update failed.") from exc