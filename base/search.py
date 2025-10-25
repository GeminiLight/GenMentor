"""Web search and crawling utilities used across GenMentor."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable, Literal, Sequence

import requests
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    AsyncChromiumLoader,
    AsyncHtmlLoader,
)
from langchain_community.document_transformers import Html2TextTransformer

from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

LoaderName = Literal["html", "chromium"]
TransformerName = Literal["beautiful_soup", "html2text"]

DEFAULT_TIMEOUT = 15
SESSION = requests.Session()


@dataclass(slots=True)
class MainContentExtractor:
    """Simplified HTML parser that keeps key page content."""

    include_title: bool = True

    def transform_documents(self, docs: Iterable[Document]) -> list[Document]:
        transformed_docs: list[Document] = []

        for doc in docs:
            try:
                parser = _MainContentHTMLParser(include_title=self.include_title)
                parser.feed(doc.page_content or "")
                parser.close()

                parts: list[str] = []
                title = parser.get_title()
                if title:
                    parts.append(title)

                parts.extend(parser.get_paragraphs())

                if parts:
                    transformed_docs.append(
                        Document(
                            page_content="\n\n".join(parts),
                            metadata=dict(getattr(doc, "metadata", {}) or {}),
                        )
                    )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Failed to parse document: %s",
                    exc,
                    exc_info=logger.isEnabledFor(logging.DEBUG),
                )

        return transformed_docs


class _MainContentHTMLParser(HTMLParser):
    __slots__ = (
        "include_title",
        "_capture_title",
        "_capture_paragraph",
        "_current_paragraph",
        "_paragraphs",
        "_title_parts",
    )

    def __init__(self, *, include_title: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.include_title = include_title
        self._capture_title = False
        self._capture_paragraph = False
        self._current_paragraph: list[str] = []
        self._paragraphs: list[str] = []
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: D401 - HTMLParser signature
        if self.include_title and tag == "title":
            self._capture_title = True
        if tag == "p":
            self._capture_paragraph = True
            self._current_paragraph = []

    def handle_endtag(self, tag: str) -> None:
        if self.include_title and tag == "title":
            self._capture_title = False
        if tag == "p" and self._capture_paragraph:
            self._capture_paragraph = False
            text = _clean_text("".join(self._current_paragraph))
            if text:
                self._paragraphs.append(text)
            self._current_paragraph = []

    def handle_data(self, data: str) -> None:
        if not data:
            return
        if self._capture_title:
            self._title_parts.append(data)
        elif self._capture_paragraph:
            self._current_paragraph.append(data)

    def get_title(self) -> str:
        if not self.include_title:
            return ""
        return _clean_text(" ".join(self._title_parts))

    def get_paragraphs(self) -> list[str]:
        return self._paragraphs.copy()


class _BodyTextHTMLParser(HTMLParser):
    __slots__ = ("_skip_stack", "_chunks")

    _BLOCK_TAGS = {
        "article",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "nav",
        "p",
        "section",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_stack: list[str] = []
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: D401 - HTMLParser signature
        tag = tag.lower()
        if tag in {"script", "style"}:
            self._skip_stack.append(tag)
        elif tag in self._BLOCK_TAGS and not self._skip_stack:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._skip_stack and self._skip_stack[-1] == tag:
            self._skip_stack.pop()
        elif tag in self._BLOCK_TAGS and not self._skip_stack:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        if data:
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        lines = [line.strip() for line in raw.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def load_websites(
    urls: str | Sequence[str],
    *,
    loader: LoaderName = "html",
    transformer: TransformerName = "beautiful_soup",
) -> list[Document]:
    """Load and transform web pages into LangChain documents.

    Args:
        urls: A URL string or sequence of URLs to ingest.
        loader: Strategy used to fetch the pages. ``"html"`` uses an HTTP loader,
            while ``"chromium"`` executes the page in a headless browser.
        transformer: Post-processing strategy. ``"beautiful_soup"`` extracts title
            and paragraphs; ``"html2text"`` converts everything to plain text.

    Returns:
        A list of processed :class:`langchain_core.documents.Document` instances.
    """

    url_list = [urls] if isinstance(urls, str) else list(urls)
    if not url_list:
        return []

    if loader not in {"html", "chromium"}:
        raise ValueError("loader must be one of {'html', 'chromium'}")

    if transformer not in {"beautiful_soup", "html2text"}:
        raise ValueError("transformer must be one of {'beautiful_soup', 'html2text'}")

    loader_instance = AsyncHtmlLoader(url_list) if loader == "html" else AsyncChromiumLoader(url_list)
    documents = loader_instance.load()

    transformer_instance = MainContentExtractor() if transformer == "beautiful_soup" else Html2TextTransformer()
    transformed = transformer_instance.transform_documents(documents)
    # Html2TextTransformer may return a Sequence; normalize to list for callers
    return list(transformed)


# def bing_search(
#     query: str,
#     *,
#     offset: int = 0,
#     count: int = 50,
#     safe_search: Literal["Off", "Moderate", "Strict"] = "Strict",
#     timeout: int = DEFAULT_TIMEOUT,
# ) -> dict:
#     """Perform a Bing Web Search using the REST API."""

#     subscription_key = _get_env_var("BING_SUBSCRIPTION_KEY")
#     search_url = _get_env_var("BING_SEARCH_URL")

#     headers = {"Ocp-Apim-Subscription-Key": subscription_key}
#     params = {
#         "q": query,
#         "textDecorations": False,
#         "textFormat": "Raw",
#         "count": count,
#         "safeSearch": safe_search,
#         "offset": offset,
#     }

#     try:
#         response = SESSION.get(search_url, headers=headers, params=params, timeout=timeout)
#         response.raise_for_status()
#     except requests.RequestException as exc:  # pragma: no cover - network
#         raise RuntimeError(f"Bing search failed: {exc}") from exc

#     return response.json()


def browse_url(url: str, *, timeout: int = DEFAULT_TIMEOUT) -> str | None:
    """Fetch a URL and return its body text, or ``None`` on failure."""

    try:
        response = SESSION.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network
        logger.warning("Failed to fetch '%s': %s", url, exc)
        return None

    parser = _BodyTextHTMLParser()
    parser.feed(response.text)
    parser.close()

    text = parser.text()
    return text or None


__all__ = [
    "LoaderName",
    "MainContentExtractor",
    "TransformerName",
    "browse_url",
    "load_websites",
]


