from functools import partial
import logging
from typing import Any

from crawler.crawlers.crawler import Crawler
from crawler.crawlers.factory import ValidatorFactory
from crawler.session.session import SessionManager, new_session
from crawler.strategies.factory import StrategyFactory
from crawler.strategies.interfaces import Strategy
from crawler.strategies.page import Page, make_pages
from crawler.strategies.plan import Plan
from crawler.stubs.interfaces import Core, Planner, Storage

from lib.config.config import Config
from lib.logger import logger
from lib.stubs.interfaces import Stub
from lib.stubs.factory import StubFactory
from lib.logger.logger import log

# This is here to register the different implementations of the stubs.
from crawler.stubs import core, planner, storage


class StrategyNotFound(Exception):
    pass

def get_strategy(
    model: str, plan: Plan, session: SessionManager, storage: Storage
) -> Strategy | None:
    
    strategy: Strategy = StrategyFactory.get_strategy(model)
    if not strategy:
        raise StrategyNotFound

    # Get the validators
    plan_validators: dict[Any, Any] = plan.section(model, "validators")
    validators = ValidatorFactory.create_validators(plan_validators)

    # Get the crawling options for the model
    options: dict = plan.section(model, "options", False)
    model_options = options.get(model) or {}

    # Make the crawler
    crawler: Crawler = Crawler(
        validators=validators, **plan.data.get("meta"), **model_options
    )

    kwargs: dict[Any, Any] = dict(
        crawler=crawler, session=session, storage=storage, model=model
    )

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
        log.info(f"{len(pending)} pending {model}(s)")

        # Get the strategy
        strat = get_strategy(**kwargs, storage=storage, model=model)
        strat.start(pages=pending, check=False)  # Do not check the pages

        # Repeat until there are no more pending
        pending: list[Page] = storage.pending(market=market, model=model)


def start(storage: Storage, core: Core, planner: Planner) -> str:
    """Build the strategies and start the crawl"""

    while True:
        # Ask again for a market
        market = core.market()
        if not market:
            break

        # Build the plan
        plan: Plan = planner.get_plan(market)
        if not plan:
            continue

        # Create a new session instance
        session: SessionManager = new_session(cookies_fn=core.cookies)
        session.auth(market)

        # Stablish some common ground
        common: dict = dict(
            plan=plan,
            session=session,
            storage=storage,
        )
        pending = partial(pending_loop, market=market, **common)

        # Pending
        models = ["vendor","product"]
        for model in models:
            pending(model=model)

        # Build the strategy to crawl `categories`
        sects = plan.section("category", "pages")
        pages = make_pages(sects)

        categories_strat = get_strategy(**common, model="category")
        categories_strat.start(pages=pages)

    # TODO: Add a summary here

def set_logger(name: str, verbose) -> logging.Logger:
    """Configure the logger options for this application"""

    # Logger to be used on the application
    logging.setLoggerClass(logger.ColoredLogger)

    lg: logging.Logger = logging.getLogger(name)

    verbose_level = logging.getLevelName(verbose)
    lg.setLevel(verbose_level)

    logger.set_logger(lg)

    return lg

def load_flags(cfg: Config) -> None:
    """Parse the configuration and flags"""
    
    # Set a new logger for this service
    set_logger(cfg.host.name, cfg.verbose)

    # Build the communication channels with the other stubs
    stubs: dict[str, Stub] = dict()
    for client in cfg.clients.values():
        stub = StubFactory.create_stub(client)
        
        if stub:
            stubs[client.name] = stub

    # Start the crawler
    start(**stubs)


    

    