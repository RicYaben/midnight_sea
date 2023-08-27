import logging

from lib.conf.config import ServiceConfig
from lib.logger import logger
from lib.client.client import build_clients, Clients

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

def load_flags(cfg: ServiceConfig) -> None:
    """Parse the configuration and flags"""
    
    # Set a new logger for this service
    set_logger(cfg.service, cfg.verbose)

    # Build the communication channels with the other stubs
    stubs: Clients = build_clients()
    dict_stubs: dict = {stub: stubs.get_stub(stub) for stub in cfg.allowedServices}

    # Start the crawler
    strat(**dict_stubs)


    

    