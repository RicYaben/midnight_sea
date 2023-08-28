# Copyright 2023 Ricardo Yaben
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This Package contains a Crawler handler that will decide how to perform the crawling
"""
import os
import urllib.parse

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, Sequence

from lib.logger.logger import log
from lib.scraper.scraper import Scraper

from crawler.session.session import SessionManager


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
class ValidatorFactory:
    validators = {}

    @classmethod
    def get_validator(cls, validator: str) -> Validator:
        return cls.validators.get(validator)

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Validator) -> Validator:
            cls.validators[name] = decorator_cls
            return decorator_cls

        return decorator


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
    invalid: Sequence[dict[Any, Any]] = field(default_factory=list)
    required: Sequence[dict[Any, Any]] = field(default_factory=list)

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


def get_validators(validators: dict[Any, Any]) -> dict[str, Sequence[Validator]]:
    """Wrapper for the validators that returns a dictionary with the validators already set.

    Args:
        validators (dict[Any, Any]): Dictionary containing the structure of the validators

    Returns:
        dict[str, Sequence[Validator]]: Dictionary with the validators separated by their model
    """
    ret: dict = dict()

    for section_validators in validators:
        for key, val in validators[section_validators].items():
            validator = ValidatorFactory.get_validator(key)
            validator = validator(**val)

            if section_validators not in ret:
                ret[section_validators] = []

            ret[section_validators].append(validator)

    return ret


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


@dataclass
class Crawler(CrawlerProtocol):
    def crawl(self, session: SessionManager, url: str, validate: bool = True):
        """Crawls the content of some page and returns the response"""
        # Clean the url
        clean = self.clean(url)

        # Request the page
        response = session.request(clean)

        # Validate the response if necessary
        if not validate:
            return

        # If there is a response continue, otherwise
        # try again without validation this time
        if not response:
            return self.crawl(session=session, url=url, validate=False)

        valid = self.validate(response)
        if valid:
            return response

        log.info(f"URL: {url}\nCLEAN: {clean}")
        with open(os.path.join("dist", "response.html"), "wb") as f:
            f.write(response.content)
            
        # Re-authenticate if the response is not valid
        session.auth(self.market)
        return self.crawl(session=session, url=url, validate=False)

    def validate(self, response) -> bool:
        """Validates the response"""
        for section_validators in self.validators.values():
            for validator in section_validators:
                valid = validator.isValid(response)
                if not valid:
                    return False

        return True

    def clean(self, url: str) -> str:
        """Simple clean method to add the URL domain"""
        # Remove starting paths
        url = url[1:] if url.startswith("/") else url
        res = ""

        if self.path:
            url = url + self.path

        # Build the url
        for path in [self.domain, url]:
            res = urllib.parse.urljoin(res, path)

        return res
