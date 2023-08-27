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


from typing import Any

from lib.scraper.scraper import Scraper
from lib.scraper.factory import ScraperFactory
from scraper.scraper.blueprint import Blueprint, get_blueprint

@ScraperFactory.register("simple")
class SimpleScraper(Scraper):
    """Scraper for 'simple' tagged structures"""

    def scrape(self, structure: list[dict[Any, Any]]) -> dict[Any, Any]:
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

    def scrape(self, structure: list[dict[Any, Any]]) -> dict[Any, Any]:
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
) -> dict[Any, Any]:
    """Wrapper function that returns a dictionary with the content of the page

    Args:
        market (str): Market name
        model (str): Type of the content
        data (bytes): Page data

    Returns:
        dict[Any, Any]: Page content
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
    content: dict[Any, Any] = scraper.scrape(structure=blueprint.structure["struct"])
    return content
