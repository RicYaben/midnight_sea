import logging

from lib.conf.config import Config
from lib.logger import logger
from lib.stubs.interfaces import Stub
from lib.stubs.factory import StubFactory

from crawler.strategies.strategy import strat

def set_logger(name: str, verbose: str) -> logger.Logger:
    """Configure the logger options for this application"""

    # Logger to be used on the application
    logging.setLoggerClass(logger.ColoredLogger)

    lg: logging.Logger = logging.getLogger(name)

    verbose_level = logging.getLevelName(verbose)
    lg.setLevel(verbose_level)

    logger.setLogger(lg)

    return lg

def load_flags(cfg: Config) -> None:
    """Parse the configuration and flags"""
    
    # Set a new logger for this service
    set_logger(cfg.service, cfg.verbose)

    # Build the communication channels with the other stubs
    stubs: dict[str, Stub] = dict()
    for client in cfg.clients:
        stub: Stub = StubFactory.create_stub(client)

        if stub:
            stubs[client.name] = stub

    # Start the crawler
    strat(**stubs)


    

    