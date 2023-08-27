
from dataclasses import dataclass, field
from crawler.strategies.page import Page
from crawler.session.session import SessionManager
from typing import Any, Protocol

from crawler.crawlers.crawler import Crawler
from crawler.stubs.interfaces import Storage


@dataclass
class Strategy(Protocol):
    session: SessionManager
    model: str
    storage: Storage
    crawler: Crawler
    elements: list[dict[Any, Any]] = field(default_factory=list)

    def start(self, pages: list[Page]) -> list[Page]:
        """Starting point for the strategy, the only method that should be used
        by any other interface.
        It accepts a list of `Pages`.

        Args:
            pages (list[Page]): List of seed pages to crawl

        Returns:
            list[Page]: Pages stored
        """
        raise NotImplementedError