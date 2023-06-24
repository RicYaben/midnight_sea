"""
Main entrypoint for the application
"""
from ms_crawler.client.stubs import Stubs, build_stubs
from ms_crawler.globals import ALLOWED
from ms_crawler.strategies.strategy import strat


def main():
    # Build the stubs
    stubs: Stubs = build_stubs()

    stubs: dict = {stub: stubs.get_stub(stub) for stub in ALLOWED}

    # Start the crawler
    strat(**stubs)


if __name__ == "__main__":
    main()
