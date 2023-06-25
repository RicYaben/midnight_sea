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

"""
Global variables and settigns for the DNM Scraper Service
"""

import logging
import os
from typing import Sequence

from ms_scraper.logger import ColoredLogger

SERVICE = os.getenv("SERVICE", "scraper")
PROJECT = os.getenv("PROJECT", "ms")

# Logger to be used on the application
logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger("_".join([PROJECT, SERVICE]))

VERBOSE = os.getenv("VERBOSE", "DEBUG")
verbose_level = logging.getLevelName(VERBOSE)
logger.setLevel(verbose_level)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Exposed port for the application to run on
PORT = os.getenv("PORT", 2201)

# Volume in where to find external tools
VOLUME: str = os.getenv("VOLUME", "tools/%s" % SERVICE)

# Path to the folder with the certificates
CERTS = os.path.join(VOLUME, "certs")

# List of allowed services that we want to interact with
ALLOWED: Sequence[str] = ["storage"]

SERVICES = {
    service: {
        "host": os.environ.get(f"{service.upper()}_HOST"),
        "port": os.environ.get(f"{service.upper()}_PORT"),
    }
    for service in ALLOWED
}

# Blueprints
BLUEPRINTS = os.getenv("BLUEPRINTS", f"{VOLUME}/blueprints")
