from dataclasses import dataclass, field
from typing import Any
from crawler.crawlers.factory import ValidatorFactory
from crawler.crawlers.interfaces import Validator

from lib.scraper.scraper import Scraper
from lib.logger.logger import log

@ValidatorFactory.register("status")
@dataclass
class StatusCodeValidator(Validator):
    invalid: int = 400

    def isValid(self, obj) -> bool:
        if not hasattr(obj, "status_code"):
            return False

        status_code = obj.status_code
        if not (status_code and status_code < self.invalid):
            return False
        return True


@ValidatorFactory.register("content")
@dataclass
class ContentValidator(Validator):
    invalid: list[dict[Any, Any]] = field(default_factory=list)
    required: list[dict[Any, Any]] = field(default_factory=list)

    def isValid(self, obj) -> bool:
        if not hasattr(obj, "text"):
            return False

        content = obj.content
        scraper = Scraper.from_html(content)

        for element in self.invalid.copy():
            instructions: list = element.get("instructions").copy()
            found = scraper.process(scraper.content, instructions=instructions)
            if found:
                log.error(f"Found invalid element: {element.get('name')}")
                return False

        for element in self.required.copy():
            instructions: list = element.get("instructions").copy()
            found = scraper.process(scraper.content, instructions=instructions)

            if not found:
                log.error(f"Failed to find required element: {element.get('name')}")
                return False

        return True