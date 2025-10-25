import os
import logging
from typing import List, Optional, Sequence

from base.embedder_factory import EmbedderFactory

from base.dataclass import SearchResult
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.embeddings import Embeddings

from base.vectorstore import split_docs
from base.searcher_factory import SearcherManager

logger = logging.getLogger(__name__)



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



def create_vectorstore(
        embedder,
        collection_name,
        persist_directory='./chroma_db', 
    ):
    try:
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedder,
            persist_directory=persist_directory,
        )
    except Exception as e:
        print(f"Collection {collection_name} already exists. Using the existing collection.")
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedder,
            persist_directory=persist_directory,
        )
    print(f'There are {vector_store._collection.count()} records in the collection')
    return vector_store



class RagManager:

    def __init__(
        self, 
        embedder: Embeddings,
        collection_name: str = "default",
        persist_directory: str = "./data/vectorstore", 
    ):
        self._default_persist_directory = persist_directory
        self.embedder = embedder
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedder,
            persist_directory=self._default_persist_directory,
        )
        logger.info("Workflow completed successfully")
        print(f"Vectorstore initialized with collection '{collection_name}' at '{self._default_persist_directory}'")
        print(f'There are {self.vectorstore._collection.count()} records in the collection')
        os.makedirs(self._default_persist_directory, exist_ok=True)

    @property
    def persist_directory(self) -> str:
        return self._default_persist_directory

    def _resolve_directory(self, persist_directory: Optional[str]) -> str:
        return persist_directory or self._default_persist_directory


if __name__ == "__main__":
    # python -m base.rag
    # Example usage
    embedder = EmbedderFactory.create(
        model="sentence-transformers/all-mpnet-base-v2", 
        model_provider="huggingface")
    rag_manager = RagManager(
        embedder=embedder,
        persist_directory="./data/vectorstore",
    )
    searcher_manager = SearcherManager(
        searcher_provider="duckduckgo",
        loader_type="web",
        max_search_results=5,
    )
    results = searcher_manager.invoke("LangChain community utilities")
    print(f"Retrieved {len(results)} search results.")

    rag_manager.vectorstore.add_documents(
        documents=[Document(page_content=res.content, metadata={"source": res.link}) for res in results],
        embedding_function=embedder,
    )
    # Further code to demonstrate functionality can be added here