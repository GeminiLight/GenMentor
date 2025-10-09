from __future__ import annotations

import abc
import json
import logging
from typing import Any, Optional, Sequence, TYPE_CHECKING

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from .llms import LLMFactory


class AbstractAgent(abc.ABC):
    """Base agent wiring a prompt to an LLM and handling structured responses."""

    def __init__(
        self,
        name: str,
        llm: Any = None,
        *,
        json_output: bool = True,
        output_tracks: bool = False,
        max_retries: int = 3,
        response_model: Optional[type[BaseModel]] = None,
        **_: Any,
    ) -> None:
        self.name = name
        self.json_output = json_output
        self.output_tracks = output_tracks
        self.max_retries = max_retries
        self.response_model = response_model

        self.prompt: Optional[ChatPromptTemplate] = None
        self.system_prompt: Optional[str] = None
        self.task_prompt: Optional[str] = None
        self._include_history = False
        self._history_variable = "history"

        self._llm_factory: Optional["LLMFactory"] = None
        self._llm_source = llm
        self.llm = llm

        if hasattr(llm, "create") and callable(getattr(llm, "create")):
            # Duck-type detection for factories (e.g., LLMFactory)
            self._llm_factory = llm  # type: ignore[assignment]
            self._llm_source = None
            self.llm = None

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def act(
        self,
        input_dict: Optional[dict[str, Any] | Sequence[dict[str, Any]]] = None,
        *,
        batch_mode: bool = False,
        response_model: Optional[type[BaseModel]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> Any:
        """Execute the agent with the given inputs."""

        return self.invoke_llm(
            input_dict=input_dict,
            batch_mode=batch_mode,
            response_model=response_model,
            config=config,
        )

    def invoke_llm(
        self,
        input_dict: Optional[dict[str, Any] | Sequence[dict[str, Any]]],
        *,
        batch_mode: bool = False,
        response_model: Optional[type[BaseModel]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> Any:
        """Invoke the underlying LLM with retry handling and post-processing."""

        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < max(self.max_retries, 1):
            try:
                raw_output = self.invoke_llm_once(
                    input_dict=input_dict,
                    batch_mode=batch_mode,
                    response_model=response_model,
                    config=config,
                )
                result = self._post_process_output(
                    raw_output,
                    batch_mode=batch_mode,
                    response_model=response_model,
                    original_input=input_dict,
                )

                if self.json_output and result is not None:
                    if batch_mode and isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
                        for single_output, single_input in zip(result, self._ensure_sequence(input_dict)):
                            if not self.check_json_output(single_output, single_input):
                                raise ValueError("JSON output validation failed for batched entry.")
                    else:
                        if not self.check_json_output(result, input_dict):
                            raise ValueError("JSON output validation failed.")

                return result

            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                attempts += 1
                last_error = exc
                logger.warning(
                    "[%s] Attempt %s/%s failed to produce valid output: %s",
                    self.name,
                    attempts,
                    self.max_retries,
                    exc,
                )

        raise RuntimeError(
            f"Failed to invoke LLM for agent '{self.name}' after {self.max_retries} attempts",
        ) from last_error

    def invoke_llm_once(
        self,
        input_dict: Optional[dict[str, Any] | Sequence[dict[str, Any]]],
        *,
        batch_mode: bool = False,
        response_model: Optional[type[BaseModel]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> Any:
        """Single invocation of the prompt/LLM stack."""

        runnable = self._build_chain(response_model=response_model, config=config)
        if batch_mode:
            return runnable.batch(self._normalize_batch_input(input_dict))
        return runnable.invoke(input_dict or {})

    def as_runnable(
        self,
        *,
        response_model: Optional[type[BaseModel]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> Runnable:
        """Expose the agent as a LangChain Runnable for LangGraph integration."""

        return self._build_chain(response_model=response_model, config=config)

    # ------------------------------------------------------------------
    # Prompt configuration helpers
    # ------------------------------------------------------------------
    def set_prompts(
        self,
        system_prompt: str,
        task_prompt: str,
        *,
        include_history: bool = False,
        history_variable: str = "history",
    ) -> None:
        """Register the prompts used by the agent."""

        self.system_prompt = system_prompt
        self.task_prompt = task_prompt
        self._include_history = include_history
        self._history_variable = history_variable

        messages: list[Any] = [("system", self.system_prompt)]
        if include_history:
            messages.append(MessagesPlaceholder(variable_name=history_variable))
        messages.append(("human", self.task_prompt))

        self.prompt = ChatPromptTemplate.from_messages(messages)

    def update_prompts(
        self,
        *,
        system_prompt: Optional[str] = None,
        task_prompt: Optional[str] = None,
        include_history: Optional[bool] = None,
        history_variable: str = "history",
    ) -> None:
        """Update prompts while preserving unset values."""

        if system_prompt is not None:
            self.system_prompt = system_prompt
        if task_prompt is not None:
            self.task_prompt = task_prompt

        include_history = (
            bool(include_history)
            if include_history is not None
            else self._include_history
        )
        history_variable = (
            self._history_variable if history_variable is None else history_variable
        )
        self.set_prompts(
            self.system_prompt or "",
            self.task_prompt or "",
            include_history=include_history,
            history_variable=history_variable,
        )

    # ------------------------------------------------------------------
    # Hooks for subclasses
    # ------------------------------------------------------------------
    def check_json_output(self, output: Any, input_dict: Any) -> bool:
        """Validate the parsed JSON output. Subclasses may override."""

        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_chain(
        self,
        *,
        response_model: Optional[type[BaseModel]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> Runnable:
        if not self.prompt:
            raise ValueError("Prompt not set. Call set_prompts before invoking the agent.")

        llm = self._resolve_llm(response_model=response_model, config=config)
        return self.prompt | llm

    def _resolve_llm(
        self,
        *,
        response_model: Optional[type[BaseModel]] = None,
        config: Optional[RunnableConfig] = None,
    ) -> Any:
        llm_candidate: Any

        if self._llm_factory is not None:
            llm_candidate = self._llm_factory.create(config=config)
            config = None
        elif self._llm_source is None:
            raise ValueError("No LLM was provided to the agent.")
        elif callable(self._llm_source):
            llm_candidate = self._llm_source()
        else:
            llm_candidate = self._llm_source

        model_schema = response_model or self.response_model
        if model_schema and hasattr(llm_candidate, "with_structured_output"):
            llm_candidate = llm_candidate.with_structured_output(model_schema)

        if config:
            llm_candidate = llm_candidate.with_config(config)

        return llm_candidate

    def _normalize_batch_input(
        self, input_data: Optional[dict[str, Any] | Sequence[dict[str, Any]]]
    ) -> Sequence[dict[str, Any]]:
        if input_data is None:
            return [{}]
        if isinstance(input_data, Sequence) and not isinstance(input_data, (str, bytes, dict)):
            return list(input_data)
        return [input_data]  # type: ignore[list-item]

    def _ensure_sequence(
        self, input_data: Optional[dict[str, Any] | Sequence[dict[str, Any]]]
    ) -> Sequence[dict[str, Any]]:
        return self._normalize_batch_input(input_data)

    def _post_process_output(
        self,
        output: Any,
        *,
        batch_mode: bool,
        response_model: Optional[type[BaseModel]],
        original_input: Optional[dict[str, Any] | Sequence[dict[str, Any]]],
    ) -> Any:
        if batch_mode:
            return [
                self._strip_tracks(self._parse_output(item, response_model=response_model))
                for item in output
            ]
        return self._strip_tracks(self._parse_output(output, response_model=response_model))

    def _parse_output(self, output: Any, *, response_model: Optional[type[BaseModel]]) -> Any:
        schema = response_model or self.response_model

        if isinstance(output, BaseModel):
            return output.model_dump()

        if schema is not None and hasattr(output, "model_dump"):
            return output.model_dump()

        if isinstance(output, dict):
            return output

        if self.json_output and schema is None:
            content = self._extract_content(output)
            if content is None:
                raise ValueError("Expected JSON output but received empty response.")
            return json.loads(self.fix_json_string(content))

        if isinstance(output, BaseMessage):
            return output.content

        return output

    @staticmethod
    def _extract_content(output: Any) -> Optional[str]:
        if output is None:
            return None
        if isinstance(output, BaseMessage):
            return output.content
        if isinstance(output, str):
            return output
        if hasattr(output, "content"):
            return getattr(output, "content")
        return str(output)

    def _strip_tracks(self, value: Any) -> Any:
        if (
            not self.output_tracks
            and isinstance(value, dict)
            and "tracks" in value
            and "result" in value
        ):
            return value.get("result", value)
        return value

    @staticmethod
    def fix_json_string(json_str: str) -> str:
        content = json_str.strip()
        if content.startswith("```"):
            content = content[3:]
            if content.lower().startswith("json"):
                content = content[4:]
            content = content.lstrip()
            if content.endswith("```"):
                content = content[:-3]
        return content.strip()


class Agent(AbstractAgent):
    """Simple agent with prompt helpers."""

    def __init__(
        self,
        name: str,
        llm: Any = None,
        *,
        json_output: bool = True,
        output_tracks: bool = False,
        tools: Optional[list[Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name,
            llm,
            json_output=json_output,
            output_tracks=output_tracks,
            **kwargs,
        )
        self.tools = tools or []