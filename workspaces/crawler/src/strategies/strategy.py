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
import re
import time
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, Protocol, Sequence

from ms_crawler.client.interfaces import Core, Planner, Storage
from ms_crawler.crawlers.crawler import Crawler, get_validators
from ms_crawler.globals import BUDGET, logger
from ms_crawler.scrape.scraper import Scraper
from ms_crawler.session.session import SessionManager, new_session
from ms_crawler.strategies.content import Page
from ms_crawler.strategies.plan import Plan
from ms_crawler.strategies.state import State
from tabulate import tabulate


@dataclass
class StrategyProtocol(Protocol):
    session: SessionManager
    storage: Storage
    crawler: Crawler
    model: str
    elements: Sequence[Dict[Any, Any]] = field(default_factory=list)

    @abstractmethod
    def start(self, pages: Sequence[Page]) -> Sequence[Page]:
        """Starting point for the strategy, the only method that should be used
        by any other interface.
        It accepts a list of `Pages`.

        Args:
            pages (Sequence[Page]): List of seed pages to crawl

        Returns:
            Sequence[Page]: Pages stored
        """
        raise NotImplementedError


@dataclass
class Strategy(StrategyProtocol):
    def start(self, pages: Sequence[Page], check=True) -> Sequence[Page]:
        stored = asyncio.run(self.run(pages=pages, check=check))
        return stored

    async def run(self, pages: Sequence[Page], check=True) -> Sequence[Page]:
        p_stored: Sequence[Page] = []

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

    def new_pages(self, pages: Sequence[Page]) -> Sequence[Page]:
        """Return only those pages not found in the db"""
        urls: Sequence[str] = [page.url for page in pages]
        db: Sequence[str] = self.check(
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

    def store(self, log=True, **kwargs):
        try:
            stored = self.storage.store(**kwargs)
            return stored
        except Exception as e:
            if log:
                logger.error(f"Something went wrong while storing. Retrying...")
            time.sleep(2)
            return self.store(log=False, **kwargs)

    def check(self, log=True, **kwargs):
        try:
            in_db = self.storage.check(**kwargs)
            return in_db
        except:
            if log:
                logger.error(f"Something went wrong while checking. Retrying...")
            time.sleep(2)
            return self.check(log=False, **kwargs)


@dataclass
class StrategyFactory:
    strategies = {}

    @classmethod
    def get_strategy(cls, strategy: str) -> Strategy:
        return cls.strategies.get(strategy, Strategy)

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Strategy) -> Strategy:
            cls.strategies[name] = decorator_cls

            return decorator_cls

        return decorator


@StrategyFactory.register("category")
@dataclass
class CategoryStrategy(StrategyProtocol):
    # [3/6/2022] TODO: This kind of strategies could be generalised to simply strategies
    # with nested pages and so on.
    # Perhaps, a nice Strategy could recognise this from the plan.
    state: State = None

    def start(self, pages: Sequence[Page]):
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
            logger.info(f"Next category page...")
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

    def get_listings(self, content) -> Sequence[str]:
        # Load the content in the scraper
        scraper: Scraper = Scraper.from_html(content)
        cp = self.elements.copy()

        # Find the listings and the next page elements
        listing_element = next(filter(lambda x: x.get("name") == "listing", cp))
        listings = self.find_elements(scraper=scraper, element=listing_element)

        nx_element = next(filter(lambda x: x.get("name") == "next_page", cp))
        next_page = self.find_elements(scraper=scraper, element=nx_element)

        return (listings, next_page)

    def crawl_listings(self, urls: Sequence[str], category: str) -> Sequence[Page]:
        pages = [Page(url=url, meta=dict(category=category)) for url in urls]

        crawler = copy.copy(self.crawler)
        crawler.validators = dict(all=crawler.validators["all"])

        strat: Strategy = Strategy(
            crawler=crawler,
            storage=self.storage,
            model="item",
            session=self.session,
        )

        # Crawl the pages asynchron.
        stored = strat.start(pages=pages)
        return stored

    def find_elements(self, scraper: Scraper, element: Dict[Any, Any]):
        """This method finds the listings on the response, and returns
        a list of url's
        """
        instructions = element.get("instructions").copy()
        ret = scraper.process(content=scraper.content, instructions=instructions)

        if not "many" in element and ret:
            ret = ret.pop(0)

        return ret


def get_strategy(
    model: str, plan: Plan, session: SessionManager, storage: Storage
) -> Strategy:
    # Get the validators
    plan_validators: Dict[Any, Any] = plan.section(model, "validators")
    validators = get_validators(plan_validators)

    # Get the crawling options for the model
    options: dict = plan.section(model, "options", False)
    options = options.get(model) or {}

    # Make the crawler
    crawler: Crawler = Crawler(
        validators=validators, **plan.data.get("meta"), **options
    )

    kwargs: Dict[Any, Any] = dict(
        crawler=crawler, session=session, storage=storage, model=model
    )

    # Get the strategy and instantiate it
    strategy: Strategy = StrategyFactory.get_strategy(model)

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
    pending: Sequence[Page] = storage.pending(market=market, model=model)

    while pending:
        logger.info(f"Got {len(pending)} pending {model}(s)")

        # Get the strategy
        strat = get_strategy(**kwargs, storage=storage, model=model)
        strat.start(pages=pending, check=False)  # Do not check the pages

        # Repeat until there are no more pending
        pending: Sequence[Page] = storage.pending(market=market, model=model)


def strat(storage: Storage, core: Core, planner: Planner) -> str:
    """Build the strategies and start the crawl"""

    # Request the market
    market: str = core.market()

    while market:
        # Build the plan
        plan: Plan = planner.plan(market)

        # Create a new session instance
        session: SessionManager = new_session(core.cookies, BUDGET)
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


@dataclass
class PageParser:
    rex = re.compile(r"\$\{(?P<var>.*?)\}")

    def parse_to_pages(self, page: dict) -> Sequence[Page]:
        path: str = page.get("path")
        ret = []

        if "vars" in page:
            vars: dict = page.get("vars")

            for key, val in vars.items():
                fn = getattr(self, f"replace_{key}")
                res = fn(path, val)
                ret += res
        else:
            ret = [path]

        name = page.get("name")
        pages = [Page(url=page, meta=dict(category=name)) for page in ret]

        return pages

    def replace_list(self, path, ls) -> list:
        ret = []
        for i in ls:
            sub = re.sub(self.rex, str(i), path)
            ret.append(sub)
        return ret

    def replace_range(self, path, ran) -> list:
        start, stop = ran
        ret = []
        for i in range(start, stop + 1):
            sub = re.sub(self.rex, str(i), path)
            ret.append(sub)
        return ret


def make_pages(sects) -> Sequence[Page]:
    # Load the pages
    ret = []
    parser = PageParser()

    for sections in sects.values():
        for page in sections:
            res: list = parser.parse_to_pages(page)
            ret += res

    return ret
