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

import logging
import os
import uuid
from typing import Sequence

import requests

from ms_crawler.logger import ColoredLogger

SERVICE = os.getenv("SERVICE", "crawler")
PROJECT = os.getenv("PROJECT", "ms")

# Logger to be used on the application
logging.setLoggerClass(ColoredLogger)

VERBOSE = os.getenv("VERBOSE", "DEBUG")
verbose_level = logging.getLevelName(VERBOSE)

logger = logging.getLogger("_".join([PROJECT, SERVICE]))
logger.setLevel(verbose_level)

logging.getLogger("filelock").setLevel(verbose_level)

requests.logging.getLogger().setLevel(verbose_level)

# Name the crawler
SERVICE_ID = os.getenv("SERVICE_ID", "%s" % str(uuid.uuid4())[:8])

# Volume in where to find external tools
VOLUME: str = os.getenv("VOLUME", "tools/%s" % SERVICE)

# List of allowed services that we want to interact with
ALLOWED: Sequence = ["storage", "core", "planner"]

# Where the services are hosted
# [1/3/2022] NOTE: This should be replaced to a query to an LDAP server at some point
# The application should not manage where these services are hosted.
# The certificates are currently being loaded from a shared drive, which is not always
# possible.
SERVICES = {
    service: {
        "host": os.environ.get(f"{service.upper()}_HOST"),
        "port": os.environ.get(f"{service.upper()}_PORT"),
    }
    for service in ALLOWED
}

# Path to the folder with the certificates
CERTS = os.path.join(VOLUME, "certs")

# Browser headers to use on each request
BROWSER_HEADERS = {
    "user-agent": os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    )
}

# Host for the proxy
PROXY_HOST = os.getenv("PROXY_HOST", "localhost")

# Budget to use during the crawl
# NOTE: Although there are other budgets, it is only recomendable to
# use the simple one
BUDGET = os.getenv("BUDGET", "simple")
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", 5))
MAX_DELAY = int(os.getenv("MAX_DELAY", 5))

# Timeout before dropping the connection
TIMEOUT: int = int(os.getenv("TIMEOUT", 60))
