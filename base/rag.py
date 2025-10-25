from dataclasses import dataclass
from typing import List, Optional, Sequence

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document

from base.vectorstore import create_vectorstore, split_docs


@dataclass
class SearchResult:
    url: str
    content: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    score: Optional[float] = None


class TavilySearchClient:
    def __init__(self, default_max_results: int = 3):
        self.default_max_results = default_max_results

    def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        effective_max = max_results or self.default_max_results
        search = TavilySearchResults(max_results=effective_max)
        print(f"Searching Tavily for: '{query}' (max_results={effective_max})...")
        raw_results = search.invoke({"query": query}) or []

        results: List[SearchResult] = []
        for item in raw_results:
            content = item.get("content") or item.get("snippet") or ""
            results.append(
                SearchResult(
                    url=item.get("url", ""),
                    content=content,
                    title=item.get("title"),
                    snippet=item.get("snippet"),
                    score=item.get("score"),
                )
            )

        if not results:
            print("No results found from Tavily.")
        else:
            print(f"Received {len(results)} documents directly from Tavily.")
        return results


class SimpleSourceProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 0, split_by: str = "token"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.split_by = split_by

    def process(
        self,
        sources: Sequence[SearchResult],
        query: str,
        *,
        chunk_size: Optional[int] = None,
    ) -> List[Document]:
        unique_docs: List[Document] = []
        seen_urls = set()

        for result in sources:
            if not result.content.strip():
                continue
            if result.url and result.url in seen_urls:
                continue

            metadata = {"source": result.url}
            if result.title:
                metadata["title"] = result.title
            if result.score is not None:
                metadata["score"] = result.score
            if result.snippet:
                metadata["snippet"] = result.snippet

            unique_docs.append(Document(page_content=result.content, metadata=metadata))
            if result.url:
                seen_urls.add(result.url)

        if not unique_docs:
            return []

        effective_chunk = chunk_size or self.chunk_size
        splits = split_docs(
            unique_docs,
            chunk_size=effective_chunk,
            chunk_overlap=self.chunk_overlap,
            split_by=self.split_by,
        )
        print(f"Prepared {len(splits)} document chunks for query '{query}'.")
        return splits


class VectorStoreManager:
    def __init__(self, persist_directory: str = "./vectorstore", embeddings_type: str = "sentence_transformer"):
        self._default_persist_directory = persist_directory
        self.embeddings_type = embeddings_type

    @property
    def persist_directory(self) -> str:
        return self._default_persist_directory

    def _resolve_directory(self, persist_directory: Optional[str]) -> str:
        return persist_directory or self._default_persist_directory

    def upsert(
        self,
        collection_name: str,
        documents: Sequence[Document],
        *,
        persist_directory: Optional[str] = None,
    ):
        directory = self._resolve_directory(persist_directory)
        vectorstore = create_vectorstore(collection_name, self.embeddings_type, directory)
        if documents:
            vectorstore.add_documents(list(documents))
            print(f"Stored {len(documents)} document chunks into collection '{collection_name}'.")
        else:
            print("No new content to add to the vector store.")
        return vectorstore

    def load(self, collection_name: str, *, persist_directory: Optional[str] = None):
        directory = self._resolve_directory(persist_directory)
        return create_vectorstore(collection_name, self.embeddings_type, directory)


class DeepSearchPipeline:
    def __init__(
        self,
        search_client: Optional[TavilySearchClient] = None,
        source_processor: Optional[SimpleSourceProcessor] = None,
        vectorstore_manager: Optional[VectorStoreManager] = None,
        retriever_k: int = 5,
        pro_mode_multiplier: int = 2,
    ):
        self.search_client = search_client or TavilySearchClient()
        self.source_processor = source_processor or SimpleSourceProcessor()
        self.vectorstore_manager = vectorstore_manager or VectorStoreManager()
        self.retriever_k = retriever_k
        self.pro_mode_multiplier = pro_mode_multiplier

    def search(self, query: str, *, max_results: Optional[int] = None, pro_mode: bool = False) -> List[SearchResult]:
        effective_max = max_results or self.search_client.default_max_results
        if pro_mode:
            effective_max = max(effective_max, self.search_client.default_max_results * self.pro_mode_multiplier)
        return self.search_client.search(query, max_results=effective_max)

    def search_and_store(
        self,
        query: str,
        collection_name: str,
        *,
        max_results: Optional[int] = None,
        pro_mode: bool = False,
        persist_directory: Optional[str] = None,
        chunk_size: Optional[int] = None,
    ):
        results = self.search(query, max_results=max_results, pro_mode=pro_mode)
        processed = self.source_processor.process(results, query, chunk_size=chunk_size)
        vectorstore = self.vectorstore_manager.upsert(
            collection_name,
            processed,
            persist_directory=persist_directory,
        )
        return vectorstore, processed

    def retrieve(
        self,
        collection_name: str,
        query: str,
        *,
        k: Optional[int] = None,
        persist_directory: Optional[str] = None,
    ):
        vectorstore = self.vectorstore_manager.load(collection_name, persist_directory=persist_directory)
        retriever = vectorstore.as_retriever(search_kwargs={"k": k or self.retriever_k})
        return retriever.invoke(query)

    def run(
        self,
        query: str,
        collection_name: str,
        *,
        max_results: Optional[int] = None,
        k: Optional[int] = None,
        pro_mode: bool = False,
        persist_directory: Optional[str] = None,
        chunk_size: Optional[int] = None,
    ):
        vectorstore, _ = self.search_and_store(
            query,
            collection_name,
            max_results=max_results,
            pro_mode=pro_mode,
            persist_directory=persist_directory,
            chunk_size=chunk_size,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k or self.retriever_k})
        return retriever.invoke(query)


def build_context(docs: Sequence[Document]) -> str:
    formatted_chunks: List[str] = []
    for idx, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title") if doc.metadata else None
        source = doc.metadata.get("source") if doc.metadata else None
        header_parts = [f"[{idx}]"]
        if title:
            header_parts.append(title)
        if source:
            header_parts.append(f"Source: {source}")
        header = " | ".join(header_parts)
        body = doc.page_content.strip()
        formatted_chunks.append(f"{header}\n{body}")
    return "\n\n".join(formatted_chunks)


def format_docs(docs: Sequence[Document]) -> str:
    return build_context(docs)


def create_deep_search_pipeline(
    *,
    persist_directory: str = "./vectorstore",
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
    split_by: str = "token",
    default_max_results: int = 3,
    retriever_k: int = 5,
    pro_mode_multiplier: int = 2,
) -> DeepSearchPipeline:
    search_client = TavilySearchClient(default_max_results=default_max_results)
    source_processor = SimpleSourceProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        split_by=split_by,
    )
    vectorstore_manager = VectorStoreManager(persist_directory=persist_directory)
    return DeepSearchPipeline(
        search_client=search_client,
        source_processor=source_processor,
        vectorstore_manager=vectorstore_manager,
        retriever_k=retriever_k,
        pro_mode_multiplier=pro_mode_multiplier,
    )


def search_and_store(
    query: str,
    db_collection_name: str,
    db_persist_directory: str = "./vectorstore",
    chunk_size: int = 1000,
    num_results: int = 3,
    *,
    pro_mode: bool = False,
):
    pipeline = create_deep_search_pipeline(
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
        default_max_results=num_results,
    )
    vectorstore, _ = pipeline.search_and_store(
        query,
        db_collection_name,
        max_results=num_results,
        pro_mode=pro_mode,
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
    )
    return vectorstore


def search_enhanced_rag(
    query: str,
    db_collection_name: str,
    db_persist_directory: str = "./vectorstore",
    num_results: int = 3,
    num_retrieval_results: int = 5,
    *,
    chunk_size: int = 1000,
    pro_mode: bool = False,
):
    pipeline = create_deep_search_pipeline(
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
        default_max_results=num_results,
        retriever_k=num_retrieval_results,
    )
    return pipeline.run(
        query,
        db_collection_name,
        max_results=num_results,
        k=num_retrieval_results,
        pro_mode=pro_mode,
        persist_directory=db_persist_directory,
        chunk_size=chunk_size,
    )