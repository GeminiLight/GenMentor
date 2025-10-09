"""Search-enhanced retrieval helpers leveraging LangGraph workflows."""

from __future__ import annotations

import csv
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence, TypedDict

from langchain_core.documents import Document
from langchain_community.utilities import BingSearchAPIWrapper

try:
    from langgraph.graph import END, StateGraph
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError(
        "langgraph is required for the RAG pipeline. Install with `pip install langgraph`."
    ) from exc

from base.search import load_websites
from base.vectorstore import create_vectorstore, split_docs

logger = logging.getLogger(__name__)


class URLCache:
    """CSV-backed cache for tracking ingested URLs per vector store collection."""

    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path
        self._ensure_cache()

    def _ensure_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            with self.cache_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["collection_name", "url"])

    def read(self, collection_name: str) -> set[str]:
        cached: set[str] = set()
        if not self.cache_path.exists():
            self._ensure_cache()
            return cached

        with self.cache_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row.get("collection_name") == collection_name and row.get("url"):
                    cached.add(row["url"])
        return cached

    def append(self, collection_name: str, urls: Sequence[str]) -> None:
        unique_urls = [url for url in urls if url]
        if not unique_urls:
            return

        with self.cache_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            for url in unique_urls:
                writer.writerow([collection_name, url])


@dataclass(slots=True)
class RAGConfig:
    """Configuration for the graph-based RAG ingestion pipeline."""

    collection_name: str
    persist_directory: Path = Path("./vectorstore")
    embeddings_type: str = "sentence_transformer"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    split_by: str = "token"
    num_results: int = 3
    cache_filename: str = "urls_cache.csv"

    def __post_init__(self) -> None:
        self.persist_directory = Path(self.persist_directory).expanduser().resolve()
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        if self.chunk_overlap >= self.chunk_size:
            logger.warning(
                "chunk_overlap (%s) must be smaller than chunk_size (%s); reducing overlap.",
                self.chunk_overlap,
                self.chunk_size,
            )
            self.chunk_overlap = max(0, self.chunk_size // 5)


class RAGState(TypedDict, total=False):
    """State container passed between LangGraph nodes."""

    query: str
    cached_urls: set[str]
    candidate_urls: list[str]
    new_urls: list[str]
    documents: list[Document]
    chunks: list[Document]
    vectorstore: Any
    errors: list[str]


@dataclass
class GraphRAGPipeline:
    """Graph-driven pipeline that performs search, crawl, split, and store operations."""

    config: RAGConfig
    search_tool: BingSearchAPIWrapper = field(default_factory=BingSearchAPIWrapper)

    def __post_init__(self) -> None:
        cache_path = self.config.persist_directory / self.config.cache_filename
        self.cache = URLCache(cache_path)
        self.vectorstore = create_vectorstore(
            self.config.collection_name,
            embeddings_type=self.config.embeddings_type,
            persist_directory=str(self.config.persist_directory),
        )
        self._graph = self._build_graph()

    @property
    def graph(self):  # pragma: no cover - thin wrapper
        return self._graph

    def run(self, query: str) -> Any:
        """Execute the workflow for a user query and return the hydrated vector store."""

        initial_state: RAGState = {
            "query": query,
            "cached_urls": self.cache.read(self.config.collection_name),
            "vectorstore": self.vectorstore,
        }
        final_state = self._graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": str(uuid.uuid4())}},
        )

        if final_state.get("errors"):
            logger.debug("RAG pipeline completed with warnings: %s", final_state["errors"])

        return self.vectorstore

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def _build_graph(self):
        workflow = StateGraph(RAGState)

        workflow.add_node("search", self._search_urls)
        workflow.add_node("filter", self._filter_urls)
        workflow.add_node("fetch", self._fetch_documents)
        workflow.add_node("split", self._split_documents)
        workflow.add_node("store", self._store_documents)

        workflow.set_entry_point("search")

        workflow.add_edge("search", "filter")
        workflow.add_conditional_edges(
            "filter",
            self._route_after_filter,
            {"ingest": "fetch", "skip": "store"},
        )
        workflow.add_edge("fetch", "split")
        workflow.add_edge("split", "store")
        workflow.add_edge("store", END)

        return workflow.compile()

    # ------------------------------------------------------------------
    # Graph nodes
    # ------------------------------------------------------------------
    def _search_urls(self, state: RAGState) -> RAGState:
        query = state["query"]
        try:
            search_results = self.search_tool.results(query, self.config.num_results)
        except Exception as exc:  # pragma: no cover - network call
            logger.warning("Search failed for '%s': %s", query, exc)
            errors = list(state.get("errors", []))
            errors.append(f"search error: {exc}")
            return {"candidate_urls": [], "errors": errors}

        urls: list[str] = []
        for item in search_results:
            link = item.get("link") if isinstance(item, dict) else None
            if link and isinstance(link, str):
                urls.append(link)

        logger.debug("Found %s candidate URLs for query '%s'", len(urls), query)
        return {"candidate_urls": urls}

    def _filter_urls(self, state: RAGState) -> RAGState:
        cached_urls = state.get("cached_urls", set())
        candidates = state.get("candidate_urls", [])
        new_urls = [url for url in candidates if url not in cached_urls]

        if not new_urls:
            logger.info("Collection '%s' already contains all %s URLs.", self.config.collection_name, len(candidates))

        return {"new_urls": new_urls}

    def _fetch_documents(self, state: RAGState) -> RAGState:
        new_urls = state.get("new_urls", [])
        if not new_urls:
            return {"documents": []}

        try:
            documents = load_websites(new_urls)
        except Exception as exc:  # pragma: no cover - network call
            logger.warning("Failed to load websites: %s", exc)
            errors = list(state.get("errors", []))
            errors.append(f"loader error: {exc}")
            return {"documents": [], "errors": errors}

        logger.debug("Loaded %s documents from %s URLs.", len(documents), len(new_urls))
        return {"documents": documents}

    def _split_documents(self, state: RAGState) -> RAGState:
        documents = state.get("documents", [])
        if not documents:
            return {"chunks": []}

        chunks = split_docs(
            documents,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            split_by=self.config.split_by,
        )
        logger.debug("Split %s documents into %s chunks.", len(documents), len(chunks))
        return {"chunks": chunks}

    def _store_documents(self, state: RAGState) -> RAGState:
        chunks = state.get("chunks", [])
        new_urls = state.get("new_urls", [])
        cached_urls = set(state.get("cached_urls", set()))

        if chunks:
            self.vectorstore.add_documents(chunks)
            self.cache.append(self.config.collection_name, new_urls)
            cached_urls.update(new_urls)
            logger.info(
                "Stored %s chunks for collection '%s'.",
                len(chunks),
                self.config.collection_name,
            )

        return {"vectorstore": self.vectorstore, "cached_urls": cached_urls}

    # ------------------------------------------------------------------
    # Routing helpers
    # ------------------------------------------------------------------
    def _route_after_filter(self, state: RAGState) -> str:
        if state.get("new_urls"):
            return "ingest"
        return "skip"


def search_and_store(
    query: str,
    db_collection_name: str,
    db_persist_directory: str | Path = "./vectorstore",
    chunk_size: int = 1000,
    num_results: int = 3,
    **kwargs: Any,
) -> Any:
    """Search web content for *query* and persist embeddings into a collection.

    Additional keyword arguments mirror :class:`RAGConfig` and allow callers to
    customise chunking, embedding backbones, and cache handling without touching
    call sites that rely on the legacy signature.
    """

    config = RAGConfig(
        collection_name=db_collection_name,
        persist_directory=Path(db_persist_directory),
        chunk_size=chunk_size,
        num_results=num_results,
        chunk_overlap=kwargs.pop("chunk_overlap", 200),
        split_by=kwargs.pop("split_by", "token"),
        embeddings_type=kwargs.pop("embeddings_type", "sentence_transformer"),
        cache_filename=kwargs.pop("cache_filename", "urls_cache.csv"),
    )

    search_tool = kwargs.pop("search_tool", None)
    if kwargs:
        unexpected = ", ".join(sorted(kwargs.keys()))
        raise TypeError(f"Unexpected keyword arguments for search_and_store: {unexpected}")

    pipeline = GraphRAGPipeline(
        config=config,
        search_tool=search_tool or BingSearchAPIWrapper(),
    )
    return pipeline.run(query)


def format_docs(docs: Iterable[Document]) -> str:
    """Format a collection of LangChain documents into a printable string."""

    return "\n\n".join(doc.page_content for doc in docs)


__all__ = [
    "GraphRAGPipeline",
    "RAGConfig",
    "URLCache",
    "format_docs",
    "search_and_store",
]
