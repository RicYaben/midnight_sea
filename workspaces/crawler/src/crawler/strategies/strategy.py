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

"""This folder contains classes and methods to plan
the crawler strategy"""

import asyncio
import copy
import time

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import Any
from crawler.strategies.factory import StrategyFactory
from crawler.strategies.interfaces import Strategy

from lib.logger import logger

from crawler.stubs.interfaces import Core, Planner, Storage
from crawler.crawlers.crawler import Crawler, get_validators
from crawler.session.session import SessionManager, new_session
from crawler.strategies.page import Page, make_pages
from crawler.strategies.plan import Plan
from crawler.strategies.state import State
from tabulate import tabulate

from lib.scraper.scraper import Scraper


@dataclass
class PageStrategy(Strategy):
    def start(self, pages: list[Page], check=True) -> list[Page]:
        stored = asyncio.run(self.run(pages=pages, check=check))
        return stored

    async def run(self, pages: list[Page], check=True) -> list[Page]:
        p_stored: list[Page] = []

        # Check the pages before crawling them
        if check:
            pages = self.new_pages(pages)

        # Crawl each page of the chunk
        while pages:
            # Get a chunk of the list
            conns = self.session.budget.connections
            chunk = pages[:conns]
            del pages[:conns]

            # Crawl the pages asynchronously but wait here until this is done
            with ThreadPoolExecutor(max_workers=len(chunk)) as executor:
                # Create the tasks

                loop = asyncio.get_event_loop()
                futures = [
                    loop.run_in_executor(executor, self.crawl_page, page)
                    for page in chunk
                ]

                # Gather the responses and print a finished thing in the console
                for response, url in await asyncio.gather(*futures):
                    res = "\u274c"  # Cross mark

                    if response and getattr(response, "content"):
                        res = "\u2714"  # Tick mark

                    print(f"[{res}] {url}")

                # Store the pages in the database
                stored = self.store(
                    pages=chunk, market=self.crawler.market, model=self.model
                )

                # Add the pages to the stored variable
                if stored:
                    p_stored += chunk

        return p_stored

    def crawl_page(self, page: Page):
        if not page.crawled:
            response = self.crawler.crawl(session=self.session, url=page.url)

            # Store the content of the response, if any
            page.store(response)
            return response, page.url

    def new_pages(self, pages: list[Page]) -> list[Page]:
        """Return only those pages not found in the db"""
        urls: list[str] = [page.url for page in pages]
        db: list[str] = self.check(
            pages=urls, model=self.model, market=self.crawler.market
        )

        # Returning pages and listings
        # We create the listings array for ease of access.
        # We are removing duplicates from here on.
        ret = []
        listings = []

        for page in pages:
            if page.url not in db and page.url not in listings:
                ret.append(page)
                listings.append(page.url)

        # Print the new items
        cols = 4
        listings = [listings[i : i + cols] for i in range(0, len(listings), cols)]
        print(f"New items: {len(ret)}\nFound items:{len(pages)}")

        if listings:
            print(tabulate(listings), "\n")

        return ret

    def store(self, **kwargs):
        try:
            stored = self.storage.store(**kwargs)
            return stored
        except Exception as e:
            logger.error(e)
            time.sleep(2)
            return self.store(**kwargs)

    def check(self, **kwargs):
        try:
            in_db = self.storage.check(**kwargs)
            return in_db
        except Exception as e:
            logger.error(e)
            time.sleep(2)
            return self.check(**kwargs)


@StrategyFactory.register("category")
@dataclass
class CategoryStrategy(Strategy):
    # [3/6/2022] TODO: This kind of strategies could be generalised to simply strategies
    # with nested pages and so on.
    # Perhaps, a nice Strategy could recognise this from the plan.
    state: State = None

    def start(self, pages: list[Page]):
        # Load the state for the market
        self.state = State(market=self.crawler.market)
        for page in pages:
            # Resume the crawling of some category page
            self.resume(page)

    def resume(self, page: Page):
        """
        +---- window -----+
        |x--- pages ------|-----------x
        +| 1 | 2 | 3 | 4 |+ 5 | 6 | 7 |
        |x----------------|-----------x
        +-----------------+
        """
        # Get the current status for the page
        category = page.meta.get(self.model)
        status: dict = self.state.get_status(category=category, path=page.url)

        # Get the window for this page. The window tells how many pages can we crawl
        # without caring about whether there is a new listing in it.
        window = self.state.calculate_window(status)

        print(
            "Resumming category crawl...\n",
            tabulate(
                [
                    [
                        window,
                        category,
                    ]
                ],
                headers=[
                    "Window",
                    "Category",
                ],
            ),
        )

        # Get the collected listings from the window
        listings: list = self.crawl(window=window, status=status, category=category)

        # If there were new listings, continue.
        if listings:
            return self.resume(page)

        else:
            status["last_crawl"] = datetime.today()
            self.state.save()

    def crawl(
        self, window: int, status: dict, category: str, listings=None
    ) -> list[str]:
        if window > 0:
            if not listings:
                listings = []

            # Check if this is the first time we are crawling this category
            # It also works for looping back to the category first page.
            url = status.get("url", None) or status.get("path")
            logger.info("Next category page...")
            print(f"- {url}")

            response = self.crawler.crawl(session=self.session, url=url)

            if hasattr(response, "content"):
                found, next_page = self.get_listings(response.content)

                # Regardless if there is a next page, set it on the status and save it.
                # This will make it so if this is the last page, the next time we crawl this
                # category, the page will be set to the first one.
                status["last"] = url
                status["url"] = next_page or None

                self.state.save()

                # Get the list of listings crawled and stored
                new_listings = self.crawl_listings(urls=found, category=category)

                if new_listings:
                    # Recalculate the window if there are new listings in the current page.
                    # This will make the window to slide
                    window = self.state.calculate_window(status)
                    listings += new_listings

                # Check if there is a next page, we crawl it, otherwise return the listings
                if next_page:
                    return self.crawl(window - 1, status, category, listings)

        return listings

    def get_listings(self, content) -> list[str]:
        # Load the content in the scraper
        scraper: Scraper = Scraper.from_html(content)
        cp = self.elements.copy()

        # Find the listings and the next page elements
        listing_element = next(filter(lambda x: x.get("name") == "listing", cp))
        listings = self.find_elements(scraper=scraper, element=listing_element)

        nx_element = next(filter(lambda x: x.get("name") == "next_page", cp))
        next_page = self.find_elements(scraper=scraper, element=nx_element)

        return [listings, next_page]

    def crawl_listings(self, urls: list[str], category: str) -> list[Page]:
        pages = [Page(url=url, meta=dict(category=category)) for url in urls]

        crawler = copy.copy(self.crawler)
        crawler.validators = dict(all=crawler.validators["all"])

        strat: PageStrategy = PageStrategy(
            crawler=crawler,
            storage=self.storage,
            model="item",
            session=self.session,
        )

        # Crawl the pages asynchron.
        stored = strat.start(pages=pages)
        return stored

    def find_elements(self, scraper: Scraper, element: dict[Any, Any]):
        """This method finds the listings on the response, and returns
        a list of url's
        """
        instructions = element.get("instructions").copy()
        ret = scraper.process(content=scraper.content, instructions=instructions)

        if ("many" not in element) and ret:
            ret = ret.pop(0)

        return ret


def get_strategy(
    model: str, plan: Plan, session: SessionManager, storage: Storage
) -> PageStrategy:
    # Get the validators
    plan_validators: dict[Any, Any] = plan.section(model, "validators")
    validators = get_validators(plan_validators)

    # Get the crawling options for the model
    options: dict = plan.section(model, "options", False)
    options = options.get(model) or {}

    # Make the crawler
    crawler: Crawler = Crawler(
        validators=validators, **plan.data.get("meta"), **options
    )

    kwargs: dict[Any, Any] = dict(
        crawler=crawler, session=session, storage=storage, model=model
    )

    # Get the strategy and instantiate it
    strategy: PageStrategy = StrategyFactory.get_strategy(model)

    # Get the strategy model unique elements
    elements: dict = plan.section(model, "elements", False)

    if elements:
        kwargs["elements"] = elements[model]

    strat = strategy(**kwargs)

    return strat


def pending_loop(market: str, model: str, storage: Storage, **kwargs):
    """Request pending pages from the database.
    This loop continues until there are no more pending items in the database

    NOTE: This need a fix, either on the database or extending this function
    to keep track of those items that are not reachable!

    Args:
        market (str): Name of the market
        model (str): Name of the model as is in the database
        storage (Storage): Storage Stub or server
    """
    pending: list[Page] = storage.pending(market=market, model=model)

    while pending:
        logger.info(f"Got {len(pending)} pending {model}(s)")

        # Get the strategy
        strat = get_strategy(**kwargs, storage=storage, model=model)
        strat.start(pages=pending, check=False)  # Do not check the pages

        # Repeat until there are no more pending
        pending: list[Page] = storage.pending(market=market, model=model)


def strat(storage: Storage, core: Core, planner: Planner) -> str:
    """Build the strategies and start the crawl"""

    # Request the market
    market: str = core.market()

    while market:
        # Build the plan
        plan: Plan = planner.plan(market)

        # Create a new session instance
        session: SessionManager = new_session(core.cookies, "simple")
        common: dict = dict(
            plan=plan,
            session=session,
            storage=storage,
        )

        # Authenticate first
        session.auth(market)

        # Pending
        models = [
            "vendor",
            "item",
        ]
        pending = partial(pending_loop, market=market, **common)

        for model in models:
            pending(model=model)

        # Build the strategy to crawl `categories`
        sects = plan.section("category", "pages")
        pages = make_pages(sects)

        categories_strat = get_strategy(**common, model="category")
        categories_strat.start(pages=pages)

        # Ask again for a market
        market = core.market()