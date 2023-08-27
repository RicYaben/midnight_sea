#!/usr/bin/python3
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

"""Generic entry point to start for DNM Scraper"""

import sys

from scraper.server.handlers import add_handlers
from scraper.server.server import build_server, read_creds, start_server


def main() -> None:
    # Read the credentials and build the server
    creds = read_creds("dist")
    server = build_server(*creds, port=0)

    # Add the endpoint handlers
    add_handlers(server)

    # Start the server
    start_server(server)


if __name__ == "__main__":
    sys.exit(main())
