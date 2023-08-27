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

import inspect
import re
from abc import abstractmethod
from dataclasses import dataclass, field
import types
from typing import Any, Dict, Protocol, Sequence

from bs4 import BeautifulSoup
from scraper.scraper.blueprint import Blueprint, get_blueprint


@dataclass
class ScraperProtocol(Protocol):
    @abstractmethod
    def scrape(self, structure: Sequence[Dict[Any, Any]]) -> Dict[Any, Any]:
        """Logic of the scrapping process"""
        raise NotImplementedError

    @abstractmethod
    def map_properties(self, prop) -> Dict[Any, Any]:
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
        instructions: Sequence[Dict[Any, Any]],
        clean_expr: str = None,
    ):
        """Wrapper for processing instructions"""
        raise NotImplementedError

    @abstractmethod
    def clean(self, data: str, expression: str = None) -> str:
        """Method to clean the results utilising a regular expression"""
        raise NotImplementedError


@dataclass
class Scraper(ScraperProtocol):
    """Base Scraper class that implements the scraper protocol

    It can not be used alone, as it does not implement the "scrape" method
    """

    content: BeautifulSoup = field(default_factory=BeautifulSoup)

    @classmethod
    def from_html(cls, html: str):
        content = BeautifulSoup(html, "lxml")
        return cls(content=content)

    def clean(self, data: str, expression: str = None) -> str:
        if expression:
            exp = re.compile(str(expression))
            groups = exp.search(data)
            if groups:
                ret = groups.group()
                data = ret

        return data

    def process(
        self,
        content,
        instructions: Sequence[Dict[Any, Any]],
        clean_expr: str = None,
    ):
        # Continue only if there is content or an instruction
        iscontent = hasattr(content, "find_all")
        if not (iscontent and instructions):
            return content

        instruction = instructions.pop(0)
        results: Sequence = []

        # Find the element(s)
        props = instruction.get("props")
        props = self.map_properties(props)
        found = content.find_all(**props)

        # Get the attribute(s)
        attrs = instruction.get("attrs", [])

        for el in found:
            for attr in attrs:
                el = self.get_attribute(content=el, attribute=attr)

            # Copy the list of instructions for each of the results
            # NOTE: It will cause the results to create branches and groups
            # of results
            cp = instructions.copy()
            branch = self.process(el, cp, clean_expr)

            # If the branch is a single value, add it to the list
            # of results, otherwise, join the list of the results
            if isinstance(branch, str):
                res = self.clean(branch, clean_expr)
                results.append(res)
            else:
                if branch:
                    results += branch

        return results

    def map_properties(self, prop) -> Dict[Any, Any]:

        if hasattr(prop, "items"):
            # Iterate through the property items
            for k, v in prop.items():

                # If the property is an object, return this method
                if isinstance(v, (dict, object)):
                    prop[k] = self.map_properties(v)

        else:
            if isinstance(prop, str):
                prop = re.compile(str(prop))

        return prop

    def get_attribute(self, content, attribute):
        # Get the attribute from the object or access the property
        attr = getattr(content, attribute, None)

        # If the attribute was a method rather than an attribute, call it.
        if inspect.ismethod(getattr(content, attribute)):
            attr = attr()

        if not attr:
            attr = content.get(attribute)

        # Remove extra spaces at both ends of the string
        if isinstance(attr, str):
            attr = attr.strip()

        return attr

    def hasmethod(self, obj, name):
        return hasattr(obj, name) and type(getattr(obj, name)) == types.MethodType


class ScraperFactory:
    scrapers = {}

    @classmethod
    def get_scraper(cls, scraper: str) -> Scraper:
        try:
            retval = cls.scrapers[scraper]
        except KeyError as err:
            raise NotImplementedError(f"{scraper=} doesn't exist") from err
        return retval

    @classmethod
    def register(cls, name):
        def decorator(decorator_cls: Scraper):
            cls.scrapers[name] = decorator_cls
            return decorator_cls

        return decorator


@ScraperFactory.register("simple")
class SimpleScraper(Scraper):
    """Scraper for 'simple' tagged structures"""

    def scrape(self, structure: Sequence[Dict[Any, Any]]) -> Dict[Any, Any]:
        # Initialise a variable to hold the data points
        data: dict = {}

        for point in structure:
            # Get the name and the instructions from the field
            instructions = point.get("instructions")
            clean = point.get("clean")
            name = point.get("name")

            # Process the instructions over the field
            value = self.process(
                content=self.content, instructions=instructions, clean_expr=clean
            )

            # If there is a value, add it to the data
            if value:
                if "many" not in point:
                    value = value.pop(0)

                data[name] = value

        return data


@ScraperFactory.register("groups")
class GroupedScraper(Scraper):
    """Scraper for content that contains groups of fields"""

    def scrape(self, structure: Sequence[Dict[Any, Any]]) -> Dict[Any, Any]:
        data: dict = {}

        for group in structure:
            # Get the name of the group and the fields
            name = group.get("name")
            clean = group.get("clean")
            fields = group.get("fields")

            if "fields" in group:
                data[name] = self.scrape(structure=fields)

            elif any(x in ["instructions", "fixed"] for x in group):
                # If there is a fixed value, use that value and jump to the next
                # iteration
                if "fixed" in group:
                    data[name] = group["fixed"]
                    continue

                # Otherwise, get the instructions and process the content
                instructions = group.get("instructions")
                value = self.process(
                    content=self.content, instructions=instructions, clean_expr=clean
                )

                if value:
                    if "many" not in group:
                        value: str = value.pop(0)

                    data[name] = value

        return data


def scrape(
    market: str,
    model: str,
    html: str | bytes,
) -> Dict[Any, Any]:
    """Wrapper function that returns a dictionary with the content of the page

    Args:
        market (str): Market name
        model (str): Type of the content
        data (bytes): Page data

    Returns:
        Dict[Any, Any]: Page content
    """
    # Load the schema of the blueprint
    blueprint: Blueprint = get_blueprint(market=market, model=model)

    # Decode the content using UTF-8
    if isinstance(html, bytes):
        html: str = html.decode("utf-8")

    # Get and instantiate the scraper
    scraper: Scraper = ScraperFactory.get_scraper(blueprint.structure["scraper"])
    scraper = scraper.from_html(html)

    # scrape the content
    content: Dict[Any, Any] = scraper.scrape(structure=blueprint.structure["struct"])

    return content
