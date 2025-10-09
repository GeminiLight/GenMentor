from __future__ import annotations

import importlib
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, ConfigDict, Field


def _freeze(value: Any) -> Any:
    """Recursively convert nested structures into hashable tuples for caching."""

    if isinstance(value, dict):
        return tuple(sorted((key, _freeze(val)) for key, val in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value

load_dotenv(override=True)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GENMENTOR_DEFAULT_MODEL", "openai:gpt-4o-mini")

LEGACY_MODEL_ALIASES: Dict[str, str] = {
    "gpt4o": "openai:gpt-4o",
    "gpt-4o": "openai:gpt-4o",
    "gpt4": "openai:gpt-4.1",
    "gpt-4": "openai:gpt-4.1",
    "gpt4o-mini": "openai:gpt-4o-mini",
    "gpt-4o-mini": "openai:gpt-4o-mini",
    "gpt4o-mini-preview": "openai:gpt-4o-mini",
    "llama": "ollama:llama3.2",
    "llama3": "ollama:llama3",
    "llama3.1": "ollama:llama3.1",
    "llama3.2": "ollama:llama3.2",
    "prometheus": "prometheus-eval/prometheus-7b-v2.0",
}

MODEL_PREFIX_TO_ENV: Dict[str, Optional[str]] = {
    "openai": "OPENAI_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "cohere": "COHERE_API_KEY",
    "ollama": None,
    "huggingface": "HUGGINGFACEHUB_API_TOKEN",
    "hf": "HUGGINGFACEHUB_API_TOKEN",
}


class LLMSettings(BaseModel):
    """Configuration used to instantiate chat models via LangChain's universal API."""

    model_config = ConfigDict(extra="forbid")

    model: str = Field(
        default=DEFAULT_MODEL,
        description="Universal model identifier, e.g. 'openai:gpt-4o-mini' or 'azure:my-deployment'.",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    api_key: Optional[str] = Field(default=None, description="Explicit API key override.")
    tags: list[str] = Field(default_factory=list, description="LangSmith tags applied via Runnable config.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata injected via Runnable config.")
    model_kwargs: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific keyword arguments.")
    enable_cache: bool = Field(default=True, description="Cache identical model instantiations.")

    def cache_key(self) -> tuple[Any, ...]:
        """Create a hashable cache key for memoising instantiated models."""

        metadata_items = _freeze(self.metadata)
        model_kwargs_items = _freeze(self.model_kwargs)
        tags_tuple = tuple(self.tags)
        return (
            self.model,
            round(self.temperature, 3),
            self.max_tokens,
            self.top_p,
            tags_tuple,
            metadata_items,
            model_kwargs_items,
        )

    def to_init_kwargs(self) -> Dict[str, Any]:
        """Transform settings into kwargs for ``init_chat_model``."""

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            **self.model_kwargs,
        }
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        if self.api_key:
            kwargs["api_key"] = self.api_key
        return kwargs


def _normalise_model_name(backbone: str) -> str:
    candidate = backbone.strip()
    return LEGACY_MODEL_ALIASES.get(candidate, candidate)


def _resolve_api_key(model_name: str) -> Optional[str]:
    provider = model_name.split(":", 1)[0].lower()
    env_var = MODEL_PREFIX_TO_ENV.get(provider)
    if env_var is None:
        return None
    return os.getenv(env_var)


def build_chat_model(settings: LLMSettings) -> BaseChatModel:
    """Construct a chat model instance from the supplied settings."""

    init_kwargs = settings.to_init_kwargs()
    if not init_kwargs.get("api_key"):
        resolved_key = _resolve_api_key(settings.model)
        if resolved_key:
            init_kwargs["api_key"] = resolved_key

    llm = init_chat_model(**init_kwargs)

    if settings.tags or settings.metadata:
        config: RunnableConfig = {}
        if settings.tags:
            config["tags"] = list(settings.tags)
        if settings.metadata:
            config.setdefault("metadata", {}).update(settings.metadata)
        llm = llm.with_config(config)

    return llm


class LLMFactory:
    """Factory with caching for creating chat models across providers."""

    def __init__(self, default_settings: Optional[LLMSettings] = None):
        self.default_settings = default_settings or LLMSettings()
        self._cache: Dict[tuple[Any, ...], BaseChatModel] = {}

    def create(
        self,
        *,
        config: Optional[RunnableConfig] = None,
        use_cache: Optional[bool] = None,
        **overrides: Any,
    ) -> BaseChatModel:
        """Instantiate a chat model, optionally overriding default settings."""

        settings = self._merge_settings(overrides)
        caching = settings.enable_cache if use_cache is None else use_cache
        cache_key = settings.cache_key()

        if caching and cache_key in self._cache:
            llm = self._cache[cache_key]
        else:
            llm = build_chat_model(settings)
            if caching:
                self._cache[cache_key] = llm

        if config:
            llm = llm.with_config(config)

        return llm

    def configurable(self, *fields: str) -> BaseChatModel:
        """Return a configurable chat model for LangGraph usage."""

        return init_chat_model(configurable_fields=fields or ("model", "max_tokens", "api_key", "temperature"))

    def _merge_settings(self, overrides: Dict[str, Any]) -> LLMSettings:
        if not overrides:
            return self.default_settings

        merged_overrides = dict(overrides)
        if "model" in merged_overrides:
            merged_overrides["model"] = _normalise_model_name(str(merged_overrides["model"]))

        if "model_kwargs" in merged_overrides and merged_overrides["model_kwargs"] is not None:
            merged_overrides["model_kwargs"] = {
                **self.default_settings.model_kwargs,
                **merged_overrides["model_kwargs"],
            }

        if "metadata" in merged_overrides and merged_overrides["metadata"] is not None:
            merged_overrides["metadata"] = {
                **self.default_settings.metadata,
                **merged_overrides["metadata"],
            }

        if "tags" in merged_overrides and merged_overrides["tags"] is not None:
            merged_overrides["tags"] = list(dict.fromkeys(self.default_settings.tags + list(merged_overrides["tags"])))

        return self.default_settings.model_copy(update=merged_overrides)


def create_hf_llm(model_type: str = "prometheus", **pipeline_kwargs: Any) -> BaseChatModel:
    """Create a Hugging Face pipeline-backed chat model for evaluation scenarios."""

    try:
        module = importlib.import_module("langchain_huggingface")
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "langchain-huggingface is required to use create_hf_llm. Install with `pip install langchain-huggingface`."
        ) from exc

    HuggingFacePipeline = getattr(module, "HuggingFacePipeline")

    model_id = LEGACY_MODEL_ALIASES.get(model_type, model_type)
    pipeline_kwargs = dict(pipeline_kwargs)
    task = pipeline_kwargs.pop("task", "text-generation")

    return HuggingFacePipeline(model_id=model_id, task=task, **pipeline_kwargs)


def create_llama_llm(model: str = "ollama:llama3.2", **kwargs: Any) -> BaseChatModel:
    """Create an Ollama-backed Llama model via the universal chat model API."""

    settings = LLMSettings(model=_normalise_model_name(model), **kwargs)
    return LLMFactory(settings).create()


def create_gpt4o_llm(deployment: Optional[str] = None, **kwargs: Any) -> BaseChatModel:
    """Create an OpenAI GPT-4o model, supporting both public and Azure deployments."""

    model_name = "openai:gpt-4o"
    if deployment:
        model_name = f"azure:{deployment}"
        os.environ.setdefault("AZURE_DEPLOYMENT", deployment)

    settings = LLMSettings(model=model_name, **kwargs)
    return LLMFactory(settings).create()


def create_llm(
    backbone: str = DEFAULT_MODEL,
    *,
    deployment: Optional[str] = None,
    config: Optional[RunnableConfig] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Create a chat model for the requested backbone using the latest LangChain APIs."""

    normalised_backbone = _normalise_model_name(backbone)

    if normalised_backbone in {"prometheus", "prometheus-eval/prometheus-7b-v2.0"}:
        return create_hf_llm(model_type=normalised_backbone, **kwargs)

    if deployment:
        normalised_backbone = f"azure:{deployment}"
        os.environ.setdefault("AZURE_DEPLOYMENT", deployment)

    settings_fields = {
        "temperature",
        "max_tokens",
        "top_p",
        "api_key",
        "tags",
        "metadata",
        "model_kwargs",
        "enable_cache",
    }

    settings_kwargs = {field: kwargs.pop(field) for field in list(kwargs.keys()) if field in settings_fields}

    if kwargs:
        unknown = ", ".join(sorted(kwargs.keys()))
        raise TypeError(f"Unsupported keyword arguments for create_llm: {unknown}")

    settings = LLMSettings(model=normalised_backbone, **settings_kwargs)
    factory = LLMFactory(settings)
    return factory.create(config=config)


__all__ = [
    "LLMSettings",
    "LLMFactory",
    "build_chat_model",
    "create_llm",
    "create_gpt4o_llm",
    "create_llama_llm",
    "create_hf_llm",
]
