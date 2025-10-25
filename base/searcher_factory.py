"""Concise provider-agnostic web search factory using LangChain community utilities.

This implementation leverages lightweight wrappers shipped with LangChain
instead of hand-written HTTP code. It supports Bing, Tavily, and Serper.dev.
"""

from __future__ import annotations

from typing import Any, Dict, List
from langchain_core.documents import Document
from .dataclass import SearchResult


class SearcherFactory:
    """Create concise searchers backed by LangChain community utilities."""

    @staticmethod
    def create(provider: str, **kwargs: Any) -> Any:
        p = (provider or "").strip().lower()
        if p in {"duckduckgo", "duck-duck-go"}:
            from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
            wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", safesearch="moderate")
        elif p in {"serper", "serper.dev", "google-serper"}:
            from langchain_community.utilities import GoogleSerperAPIWrapper
            wrapper = GoogleSerperAPIWrapper()
        elif p in {"bing", "microsoft-bing"}:
            from langchain_community.utilities import BingSearchAPIWrapper
            bing_subscription_key = kwargs.get("bing_subscription_key", None)
            bing_search_url = kwargs.get("bing_search_url", None)
            assert bing_subscription_key is not None, "bing_subscription_key is required for BingSearchAPIWrapper"
            assert bing_search_url is not None, "bing_search_url is required for BingSearchAPIWrapper"
            wrapper = BingSearchAPIWrapper(bing_subscription_key=bing_subscription_key, bing_search_url=bing_search_url)
        elif p in {"brave", "brave-search"}:
            from langchain_community.utilities import BraveSearchWrapper
            wrapper = BraveSearchWrapper()
        else:
            raise ValueError("Unsupported search provider. Choose from {'bing', 'serper', 'duckduckgo', 'brave', 'searx', 'you'}.")
        return wrapper


class SearcherManager:
    """Manager to perform searches using different providers."""

    def __init__(
            self, 
            searcher_provider: str = "duckduckgo", 
            loader_type: str = "web",
            max_search_results: int = 5,
            **kwargs: Any
        ) -> None:
        self.searcher = SearcherFactory.create(searcher_provider, **kwargs)
        self.loader_type = loader_type
        self.max_search_results = max_search_results

    def _load_urls(self, urls: List[str]) -> List[Document]:
        """Load documents from the provided URLs using the specified loader."""
        if not urls:
            return []
        if self.loader_type == "docling":
            from langchain_docling import DoclingLoader
            loader = DoclingLoader(urls)
        elif self.loader_type == "web":
            from langchain_community.document_loaders import WebBaseLoader
            loader = WebBaseLoader(urls)
        documents = loader.load()
        return documents


    def invoke(self, query: str) -> List[SearchResult]:
        """Perform a search and return structured results."""
        raw_results = self.searcher.results(query, max_results=self.max_search_results)
        urls = [item.get("link", "") for item in raw_results if item.get("link")]
        url_contents = self._load_urls(urls)
        url_docs_dict = {url: [doc for doc in url_contents if doc.metadata.get("source", "") == url] for url in urls}
        url_content_dict = {url: " ".join([doc.page_content for doc in docs]) for url, docs in url_docs_dict.items()}
        
        structured_results: List[SearchResult] = []
        for item in raw_results:
            structured_results.append(
                SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    content=url_content_dict.get(item.get("link", ""), ""),
                    snippet=item.get("snippet", None),
                    documents=url_docs_dict.get(item.get("link", ""), [])
                )
            )

        return structured_results


if __name__ == "__main__":
    # python -m base.searcher_factory
    # searcher = SearcherFactory.create(
    #     provider="duckduckgo",
    #     search_depth=1,
    #     max_results=5,
    #     include_answer=True,
    # )
    # results = searcher.results("LangChain community utilities", max_results=3)
    # print(results)
    searcher_manager = SearcherManager(
        searcher_provider="duckduckgo",
        loader_type="docling",
        max_search_results=5,
    )
    results = searcher_manager.invoke("LangChain community utilities")
    print(results)