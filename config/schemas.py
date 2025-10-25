from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMConfig:
    provider: str = "ollama"  # e.g., openai, azure-openai, ollama, anthropic, groq
    model_name: str = "llama3"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    request_timeout: int = 60


@dataclass
class SearchConfig:
    provider: str = "tavily"  # tavily, serper, bing, duckduckgo, brave, searx, you
    tavily_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    bing_subscription_key: Optional[str] = None
    bing_search_url: Optional[str] = None
    brave_api_key: Optional[str] = None
    searx_base_url: Optional[str] = None
    you_api_key: Optional[str] = None
    max_results: int = 5
    search_depth: str = "basic"  # basic | advanced


@dataclass
class VectorstoreConfig:
    persist_directory: str = "data/vectorstore"
    collection_prefix: str = "genmentor"
    embedding_model: str = "text-embedding-3-small"


@dataclass
class RAGConfig:
    chunk_size: int = 1000
    num_search_results: int = 3
    num_retrieval_results: int = 5
    allow_parallel: bool = True
    max_workers: int = 3


@dataclass
class AppConfig:
    environment: str = "dev"  # dev | staging | prod
    debug: bool = True
    log_level: str = "INFO"

    llm: LLMConfig = field(default_factory=LLMConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    vectorstore: VectorstoreConfig = field(default_factory=VectorstoreConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
