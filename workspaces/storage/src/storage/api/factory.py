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

from typing import Callable
from sqlalchemy import Sequence
from dataclasses import dataclass

from lib.logger.logger import log
from storage.database.models import Item, Page, Vendor

from storage.api.interfaces import ApiEndpoint


@dataclass
class ApiFactory:
    """Factory for the API endpoints"""

    endpoints = {}

    @classmethod
    def get_endpoint(cls, endpoint: str) -> ApiEndpoint:
        if endpoint in cls.endpoints:
            return cls.endpoints[endpoint]()

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: ApiEndpoint) -> ApiEndpoint:
            cls.endpoints[name] = decorator_cls

            return decorator_cls

        return decorator


@ApiFactory.register("page")
class PageEndpoint(ApiEndpoint):
    model = Page

    def find(self, url, market):
        try:
            instance = (
                self.db.session.query(self.model)
                .filter(self.model.market.has(name=market), self.model.url == url)
                .one_or_none()
            )

            return instance
        except:
            pass

    def placeholders(self, urls: Sequence[str], market: str, page_type: str):
        for url in urls:
            page = {"market": {"name": market}, "page_type": page_type, "url": url}
            self.store(force=False, **page)

    def exists(
        self,
        market: str,
        pages: Sequence[str],
        page_type: str,
        placeholders: bool = True,
    ):
        """Check the database for some pages.

        We do not need to know the type of the page, only the url and the market. It might
        be that two markets follow identical structure, perhaps in the future as more markets
        flower in the Dark Net, and the owners reuse their assets.

        Args:
            market (str): The market in where the pages should be found.
            pages (Sequence[str]): List of page urls
            model (str): Name of the type of the page i.e. vendor, item, etc.
            placeholders (bool): Wether or not to store the values not found as placeholders

        Returns:
            q: A query list object
        """
        log.debug("Checking pages...")
        # Filter the database to get the pages found from the list for the market
        q = (
            self.db.session.query(self.model)
            .filter(self.model.url.in_(pages), self.model.market.has(name=market))
            .all()
        )

        # Create the page placeholders for those pages that were not found
        if placeholders:
            log.debug("Creating placeholders...")

            found = [page.url for page in q]
            not_found = [url for url in pages if url not in found]
            self.placeholders(urls=not_found, market=market, page_type=page_type)

        return q

    def pending(self, market: str = None, page_type: str = None) -> list:
        """Return the list of pending pages to be crawl"""
        log.debug("Checking pending...")

        # Get the pages with no file in it
        q = self.db.session.query(self.model).filter(self.model.file == None)

        if market:
            q = q.filter(self.model.market.has(name=market))

        if page_type:
            q = q.filter(self.model.page_type == page_type)

        # Limit the query to 50 items, to make it manageable
        q = q.limit(50).all()
        return q


@ApiFactory.register("item")
class ItemEndpoint(ApiEndpoint):
    model = Item


@ApiFactory.register("vendor")
class VendorEndpoint(ApiEndpoint):
    model = Vendor
