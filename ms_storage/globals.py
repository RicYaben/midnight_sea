"""
Global variables and settigns for the DNM Storage Service
"""

import logging
import os
from typing import Sequence
from sqlalchemy.ext.declarative import declarative_base

from ms_storage.logger import ColoredLogger

SERVICE = os.getenv("SERVICE", "storage")
PROJECT = os.getenv("PROJECT", "ms")

# Logger to be used on the application
logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger("_".join([PROJECT, SERVICE]))

VERBOSE = os.getenv("VERBOSE", "DEBUG")
verbose_level = logging.getLevelName(VERBOSE)
logger.setLevel(verbose_level)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# Exposed port for the application to run on
PORT = os.getenv("PORT", 2202)

# Volume in where to find external tools
VOLUME: str = os.getenv("VOLUME", "tools/%s" % SERVICE)

# Path to the folder with the certificates
CERTS = os.path.join(VOLUME, "certs")

# Database
DATABASE_CONF = {
    "driver": os.getenv("DB_ENGINE", "psycopg2"),
    "dialect": os.getenv("DB_DIALECT", "postgresql"),
    "database": os.getenv("DB_NAME", "db"),
    "username": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

BASE = declarative_base()

# List of allowed services that we want to interact with
ALLOWED: Sequence[str] = ["scraper"]

SERVICES = {
    service: {
        "host": os.getenv(f"{service.upper()}_HOST"),
        "port": os.getenv(f"{service.upper()}_PORT"),
    }
    for service in ALLOWED
}
