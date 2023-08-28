import logging

from lib.conf.config import Config
from lib.logger import logger
from lib.stubs.interfaces import Stub
from lib.stubs.factory import StubFactory
from crawler.strategies.strategy import strat

# This is here to register the different implementations of the stubs.
from crawler.stubs import core, planner, storage

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
    strat(**stubs)


    

    