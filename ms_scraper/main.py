#!/usr/bin/python3
"""Generic entry point to start for DNM Scraper"""

import sys

from ms_scraper.globals import CERTS, PORT, SERVICE, logger
from ms_scraper.server.handlers import add_handlers
from ms_scraper.server.server import build_server, read_creds, start_server


def main() -> None:
    logger.info("Starting %s..." % SERVICE)
    # Read the credentials and build the server
    creds = read_creds(CERTS)
    server = build_server(*creds, port=PORT)

    # Add the endpoint handlers
    add_handlers(server)

    # Start the server
    start_server(server)


if __name__ == "__main__":
    sys.exit(main())
