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

"""The module contains functions that interact with the ms-storage application

This should work as a command line program in this form:

$ python -m ms_storage.commands <command name> <args>
"""

import argparse
import sys
from dataclasses import dataclass
from typing import Callable, Protocol

from storage.events import (
    calcualte_reputation,
    create_pending_vendors,
    re_scrape,
    scrape,
)
from lib.logger import logger


class Command(Protocol):
    @staticmethod
    def add_arguments():
        raise NotImplementedError

    @staticmethod
    def handle():
        raise NotImplementedError


@dataclass
class CommandFactory:
    commands = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Command) -> Command:
            # Add the command to the list
            cls.commands[name] = decorator_cls
            return decorator_cls

        return decorator

    @classmethod
    def get_command(cls, name: str) -> Command:
        if name in cls.commands:
            return cls.commands[name]


@dataclass
class CommandManager:
    parser = argparse.ArgumentParser("Commands")
    _subparsers = None

    @property
    def subparsers(self):
        if not self._subparsers:
            self._subparsers = self.parser.add_subparsers()

        return self._subparsers

    def add_arguments(self):
        # Add the parser to the subparsers
        subparsers = self.subparsers
        commands = CommandFactory.commands

        for name, command in commands.items():
            command_parser = subparsers.add_parser(name)
            command.add_arguments(command_parser)

    def handle(self, args):
        # Get the command
        command = CommandFactory.get_command(args[0])

        # Parse the commands
        parser = self.parser.parse_args(args)

        # Handle the action
        command.handle(parser)


@CommandFactory.register("rescrape")
@dataclass
class RescrapeCommand(Command):
    help: str = """
    Re-scrape the content stored for some market
    
    The following arguments can be included:
    ----------------------------------------
    @ market: str -> Name of the market to scrape
    @ extract: bool -> Whether to extract the content of the zip files
    @ keepzip: bool -> Whether to keep the Zip files after extracted
    @ page_type: str -> "vendor" or "item"
    """

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "-m",
            "--market",
            nargs="?",
            default=None,
            help="Market to Scrape",
        )

        parser.add_argument(
            "-p",
            "--page_type",
            nargs="?",
            default=None,
            help="`item` or `vendor`",
        )

        parser.add_argument(
            "-e",
            "--extract",
            action=argparse.BooleanOptionalAction,
            help="Extract the content from Zip compressed files",
        )

        parser.add_argument(
            "-k",
            "--keepzip",
            action=argparse.BooleanOptionalAction,
            help="Whether to keep the Zip file after extracting the content. This option requires 'extract'",
        )

    @staticmethod
    def handle(kwargs):
        # TODO: Fix this `build_stubs` situation
        stubs = build_stubs()
        scraper = stubs.get_stub("scraper")

        if not scraper:
            logger.error("Scraper not loaded!")
            return

        re_scrape(
            scraper=scraper,
            market=kwargs.market,
            extract=kwargs.extract,
            keep_zip=kwargs.keepzip,
            page_type=kwargs.page_type,
        )


@CommandFactory.register("create_vendors")
@dataclass
class CreateVendorPagesCommand(Command):
    help: str = """
    This command is used to create pending vendors
    """

    @staticmethod
    def add_arguments(parser):
        raise NotImplementedError

    @staticmethod
    def handle(kwargs):
        create_pending_vendors()


def parse_commands(args):
    manager = CommandManager()
    manager.add_arguments()
    manager.handle(args)


@CommandFactory.register("scrape")
@dataclass
class ScrapeCommand(Command):
    help: str = """
    This command is used to scrape files. If a market is given, only those ones will be scraped
    """

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "-m",
            "--market",
            nargs="?",
            default=None,
            help="Market to Scrape",
        )

    @staticmethod
    def handle(kwargs):
        # TODO: Fix this `build_stubs` situation
        stubs = build_stubs()
        scraper = stubs.get_stub("scraper")

        if scraper:
            scrape(scraper=scraper, market=kwargs.market)


@CommandFactory.register("reputation")
@dataclass
class CalculateReputationCommand(Command):
    help: str = """
    This command is used to calculate the reputation of the vendors.
    """

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "-m",
            "--market",
            nargs="?",
            default=None,
            help="Market vendors to calculate",
        )

    @staticmethod
    def handle(kwargs):
        calcualte_reputation(market=kwargs.market)


def parse_commands(args):
    manager = CommandManager()
    manager.add_arguments()
    manager.handle(args)


def main():
    parse_commands(sys.argv[1:])


if __name__ == "__main__":
    main()
