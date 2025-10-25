"""Concise provider-agnostic web search factory using LangChain community utilities.

This implementation leverages lightweight wrappers shipped with LangChain
instead of hand-written HTTP code. It supports Bing, Tavily, and Serper.dev.
"""

from __future__ import annotations

from typing import Any, Dict, List

# from langchain_community.utilities import (
#     BingSearchAPIWrapper,
#     GoogleSerperAPIWrapper,
#     DuckDuckGoSearchAPIWrapper,
#     BraveSearchWrapper,
#     SearxSearchWrapper,
#     YouSearchAPIWrapper
# )


class SearcherFactory:
    """Create concise searchers backed by LangChain community utilities."""

    @staticmethod
    def create(provider: str, **kwargs: Any) -> Any:
        p = (provider or "").strip().lower()
        if p in {"serper", "serper.dev", "google-serper"}:
            from langchain_community.utilities import GoogleSerperAPIWrapper
            wrapper = GoogleSerperAPIWrapper(**{k: v for k, v in kwargs.items() if k in {"serper_api_key", "k", "gl", "hl"}})
            return wrapper
        if p in {"bing", "microsoft-bing"}:
            from langchain_community.utilities import BingSearchAPIWrapper
            wrapper = BingSearchAPIWrapper(**{k: v for k, v in kwargs.items() if k in {"bing_subscription_key", "bing_search_url"}})
            return wrapper
        if p in {"duckduckgo", "duck-duck-go"}:
            from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
            wrapper = DuckDuckGoSearchAPIWrapper()
            return wrapper
        if p in {"brave", "brave-search"}:
            from langchain_community.utilities import BraveSearchWrapper
            wrapper = BraveSearchWrapper(**{k: v for k, v in kwargs.items() if k in {"brave_api_key"}})
            return wrapper
        if p in {"searx", "searxng"}:
            from langchain_community.utilities import SearxSearchWrapper
            wrapper = SearxSearchWrapper(**{k: v for k, v in kwargs.items() if k in {"searx_base_url"}})
            return wrapper
        if p in {"you", "you.com"}:
            from langchain_community.utilities import YouSearchAPIWrapper
            wrapper = YouSearchAPIWrapper(**{k: v for k, v in kwargs.items() if k in {"you_api_key"}})
            return wrapper

        raise ValueError("Unsupported search provider. Choose from {'bing', 'serper', 'duckduckgo', 'brave', 'searx', 'you'}.")

if __name__ == "__main__":
    searcher = SearcherFactory.create(
        provider="duckduckgo",
        search_depth=1,
        max_results=5,
        include_answer=True,
    )
    results = searcher.results("LangChain community utilities", max_results=3)
    print(results)