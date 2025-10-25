import os
import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters.base import TextSplitter

from base.dataclass import SearchResult
from base.embedder_factory import EmbedderFactory
from base.searcher_factory import SearcherFactory, SearchRunner
from base.rag_factory import TextSplitterFactory, VectorStoreFactory

logger = logging.getLogger(__name__)


class SearchRagManager:

    def __init__(
        self, 
        embedder: Embeddings,
        text_splitter: Optional[TextSplitter] = None,
        vectorstore: Optional[VectorStore] = None,
        search_runner: Optional[SearchRunner] = None,
        max_retrieval_results: int = 5,
    ):
        self.embedder = embedder
        self.text_splitter = text_splitter
        self.vectorstore = vectorstore
        self.search_runner = search_runner
        self.max_retrieval_results = max_retrieval_results

    def search(self, query: str) -> List[SearchResult]:
        if not self.search_runner:
            raise ValueError("SearcherRunner is not initialized.")
        results = self.search_runner.invoke(query)
        return results

    def add_documents(self, documents: List[Document]) -> None:
        if not self.vectorstore:
            raise ValueError("VectorStore is not initialized.")
        documents = [doc for doc in documents if len(doc.page_content.strip()) > 0]
        if self.text_splitter:
            split_docs = self.text_splitter.split_documents(documents)
        else:
            split_docs = documents
        self.vectorstore.add_documents(split_docs, embedding_function=self.embedder)
        logger.info(f"Added {len(split_docs)} documents to the vectorstore.")

    def retrieve(self, query: str, k: Optional[int] = None) -> List[Document]:
        k = k or self.max_retrieval_results
        if not self.vectorstore:
            raise ValueError("VectorStore is not initialized.")
        retrieval = self.vectorstore.similarity_search(query, k=k)
        return retrieval

    def invoke(self, query: str) -> List[Document]:
        results = self.search(query)
        documents = [res.document for res in results if res.document is not None]
        self.add_documents(documents=documents)
        retrieved_docs = self.retrieve(query)
        return retrieved_docs


def format_docs(docs):
    return "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in docs
    )


if __name__ == "__main__":
    # python -m base.search_rag
    embedder = EmbedderFactory.create(
        model="sentence-transformers/all-mpnet-base-v2",
        model_provider="huggingface"
    )

    searcher = SearcherFactory.create(
        provider="duckduckgo",
        max_results=5,
    )

    search_runner = SearchRunner(
        searcher=searcher,
        loader_type="web",
        max_search_results=5,
    )

    text_splitter = TextSplitterFactory.create(
        splitter_type="recursive_character",
        chunk_size=1000,
        chunk_overlap=0,
    )

    vectorstore = VectorStoreFactory.create(
        vectorstore_type="chroma",
        collection_name="example_collection",
        persist_directory="./data/vectorstore",
        embedder=embedder,
    )

    rag_manager = SearchRagManager(
        embedder=embedder,
        text_splitter=text_splitter,
        vectorstore=vectorstore,
        search_runner=search_runner,
    )

    results = rag_manager.search("LangChain community utilities")
    print(f"Retrieved {len(results)} search results.")
    documents = [res.document for res in results if res.document is not None]
    rag_manager.add_documents(documents=documents)

    retrieved_docs = rag_manager.retrieve("LangChain community utilities", k=5)
    print(f"Retrieved {len(retrieved_docs)} documents from vectorstore.")
    print(format_docs(retrieved_docs))