from crawler.session.session import SessionManager
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import Any, Protocol

@dataclass
class Validator(Protocol):
    """Validator class for the crawler responses

    The protocol suggests a single method `isValid` which takes a
    generic object and returns a boolean representation of the validity.

    The validator contains an attribute `invalid` to check
    against that must be filled when instantiated.

    The validator may contain instances of `required` values.
    """

    invalid: Any
    required: Any = None

    @abstractmethod
    def isValid(self, obj: Any) -> bool:
        raise NotImplementedError
    
@dataclass
class CrawlerProtocol(Protocol):
    market: str
    domain: str
    validators: dict[Any, Validator] = field(default_factory=dict)

    # Extra options. Modifiable when initialised
    path: str = field(default_factory="")

    @abstractmethod
    def crawl(self, session: SessionManager, url: str, retry: bool = True):
        raise NotImplementedError

    @abstractmethod
    def validate(self, response) -> bool:
        raise NotImplementedError