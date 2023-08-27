# Copyright 2023 Ricardo Yabenfield
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
from dataclasses import dataclass, field
import types
from typing import Any

from bs4 import BeautifulSoup


@dataclass
class Scraper:
    """Base Scraper class that implements the scraper protocol"""
    # TODO: Add the scrape method

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
        instructions: list[dict[Any, Any]],
        clean_expr: str = None,
    ):
        # Continue only if there is content or an instruction
        iscontent = hasattr(content, "find_all")
        if not (iscontent and instructions):
            return content

        instruction = instructions.pop(0)
        results: list = []

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
            if branch:
                if isinstance(branch, list):
                    results += branch
                else:
                    if isinstance(branch, str):
                        branch = self.clean(branch, clean_expr)
                    results.append(branch)

        return results

    def map_properties(self, prop) -> dict[Any, Any]:

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
