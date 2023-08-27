from abc import abstractmethod
import dataclasses
from typing import Any


@dataclasses
class ScraperProtocol(Protocol):
    @abstractmethod
    def scrape(self, structure: list[dict[Any, Any]]) -> dict[Any, Any]:
        """Logic of the scrapping process"""
        raise NotImplementedError

    @abstractmethod
    def map_properties(self, prop) -> dict[Any, Any]:
        """Map the properties to include regular expressions"""
        raise NotImplementedError

    @abstractmethod
    def get_attribute(self, content, attribute):
        """Get some attribute from content"""
        raise NotImplementedError

    @abstractmethod
    def process(
        self,
        content,
        instructions: list[dict[Any, Any]],
        clean_expr: str = None,
    ):
        """Wrapper for processing instructions"""
        raise NotImplementedError

    @abstractmethod
    def clean(self, data: str, expression: str = None) -> str:
        """Method to clean the results utilising a regular expression"""
        raise NotImplementedError