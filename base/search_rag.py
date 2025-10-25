import os
import logging
from typing import List, Optional, Sequence

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters.base import TextSplitter

from base.dataclass import SearchResult
from base.embedder_factory import EmbedderFactory
from base.searcher_factory import SearcherFactory, SearchRunner

logger = logging.getLogger(__name__)


class TextSplitterFactory:
    """
    Factory class to create text splitter instances based on specified type.
    
    Supported splitter types:
    - "recursive_character": Recursive character-based text splitter.
    - "character": Character-based text splitter.
    - "spacy": SpaCy-based text splitter.
    """

    @staticmethod
    def create(
        splitter_type: str = "recursive_character",
        chunk_size: int = 1000,
        chunk_overlap: int = 0,
    ) -> TextSplitter:
        splitter_type = splitter_type.lower()
        if splitter_type in ["recursive_character"]:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        elif splitter_type in ["character"]:
            from langchain_text_splitters import CharacterTextSplitter
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                encoding_name="cl100k_base", chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
        elif splitter_type in ["spacy"]:
            from langchain_text_splitters import SpacyTextSplitter
            text_splitter = SpacyTextSplitter(chunk_size=chunk_size)
        else:
            raise ValueError(f"Unsupported text splitter type: {splitter_type}")
        return text_splitter


class VectorStoreFactory:

    @staticmethod
    def create(
        vectorstore_type: str = "chroma",
        collection_name: str = "default",
        persist_directory: str = "./data/vectorstore",
        embedder: Optional[Embeddings] = None,
    ) -> VectorStore:
        vectorstore_type = vectorstore_type.lower()
        if vectorstore_type in ["chroma"]:
            from langchain_chroma import Chroma
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embedder,
                persist_directory=persist_directory,
            )
            logger.info(f'There are {vectorstore._collection.count()} records in the collection')
        else:
            raise ValueError(f"Unsupported vectorstore type: {vectorstore_type}")
        return vectorstore


class SearchRagManager:

    def __init__(
        self, 
        embedder: Embeddings,
        text_splitter: Optional[TextSplitter] = None,
        vectorstore: Optional[VectorStore] = None,
        search_runner: Optional[SearchRunner] = None,
    ):
        self.embedder = embedder
        self.text_splitter = text_splitter
        self.vectorstore = vectorstore
        self.search_runner = search_runner

    def search(self, query: str) -> List[SearchResult]:
        if not self.search_runner:
            raise ValueError("SearcherRunner is not initialized.")
        results = self.search_runner.invoke(query)
        return results

    def add_documents(self, documents: List[Document]) -> None:
        if not self.vectorstore:
            raise ValueError("VectorStore is not initialized.")
        if self.text_splitter:
            split_docs = self.text_splitter.split_documents(documents)
        else:
            split_docs = documents
        self.vectorstore.add_documents(split_docs, embedding_function=self.embedder)
        logger.info(f"Added {len(split_docs)} documents to the vectorstore.")

    def search_and_store(self, query: str) -> None:
        results = self.search(query)
        documents = [res.document for res in results if res.document is not None]
        self.add_documents(documents=documents)

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
    import pdb; pdb.set_trace()
    documents = [res.document for res in results if res.document is not None]
    rag_manager.add_documents(documents=documents)

