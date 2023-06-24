#!/usr/bin/python3
"""Generic entry point to start for DNM Storage"""

import sys
import multiprocessing
import time
from ms_storage.client.client import build_stubs
from ms_storage.database.database import get_database
from ms_storage.events import scrape

from ms_storage.globals import *
from ms_storage.server.handlers import add_handlers
from ms_storage.server.server import build_server, read_creds, start_server

"""
def scrape_event_loop():
    logger.info("Starting scrape event loop...")
    scraper = build_stubs().get_stub("scraper")

    while True:
        scrape(scraper=scraper)
        time.sleep(30)
"""


def main() -> None:
    logger.info("Starting %s..." % SERVICE)
    # Read the credentials and build the server
    creds = read_creds(CERTS)
    server = build_server(*creds, port=PORT)

    # Add the endpoint handlers
    add_handlers(server)

    # Create a database connection and load the models
    get_database()

    # Start the server
    server = multiprocessing.Process(target=start_server, args=(server,))
    server.start()

    # Scrape event loop
    #s_loop = multiprocessing.Process(target=scrape_event_loop)
    #s_loop.start()

    # Block the main process until the server dies and the scraping dies
    server.join()
    #s_loop.join()


if __name__ == "__main__":
    sys.exit(main())
