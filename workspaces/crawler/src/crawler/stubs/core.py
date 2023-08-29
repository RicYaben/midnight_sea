# Copyright 2023 Ricardo YabenAny
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

from dataclasses import dataclass
import json
import os

from typing import Any

from google.protobuf import message, json_format

from lib.logger.logger import log
from lib.stubs.factory import StubFactory

from crawler.stubs.interfaces import Core
from lib.protos.crawler_pb2_grpc import CrawlerStub
from lib.protos.crawler_pb2 import CookiesRequest, MarketRequest
from lib.stubs.interfaces import LocalStubCls


@StubFactory.register("core")
@dataclass
class CoreService(Core):
    _stub_cls = CrawlerStub
    _timeout: int = 600  # 10 min

    def __init__(self, host: str, port: int, cert: bytes) -> None:
        super().__init__(host, port, cert)

    def cookies(self, market: str) -> dict[Any, Any]:
        log.info("Requesting new cookies, this might need attention!")

        # Request for cookies to the stub
        request = CookiesRequest(market=market)
        response = self.stub.GetCookies(request, timeout=self._timeout)
        cookies: message = response.cookies
        ret = json_format.MessageToDict(cookies)

        log.info("Resumming...")

        return ret

    def market(self) -> str | None:
        """Request the market to the stub"""
        log.info("Requesting Market...")

        # Get the market once
        req = MarketRequest(stub=0)
        response = self.stub.WaitForMarket(req, timeout=self._timeout)

        # Send back the response
        return response.market


@StubFactory.register("core", True)
@dataclass
class LocalCoreService(Core):
    """Local Core Service.

    Interacts with the host shell to prompt for the market and cookies
    """
    _stub_cls = LocalStubCls
    
    TIMEOUT = 30  # Seconds
    FILENAME: str = "cookies.json"

    def _cookies_content(self, market):
        """Returns the content of the cookies file"""
        folder = os.path.join("local", "markets", market)

        # Create the folders if they do not exist
        if not os.path.exists(folder):
            os.makedirs(folder)

        filepath = os.path.join(folder, self.FILENAME)

        # Create the file if it does not exists
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            with open(filepath, "w") as file:
                json.dump({}, file)

        # Open the file and return the content
        with open(filepath, "r") as f:
            data = json.load(f)
            return data

    def cookies(self, market: str) -> dict[Any, Any]:
        """Builds cookies from a given file"""
        ticket = self.Ticket()
        self.add_ticket(ticket)

        self.lock.acquire()
        if ticket.value is not None:
            return ticket.value

        log.info("""
            Market %s needs authentication
            When you are ready, introduce any value. If you rather skip this link, introduce `skip`" 
            """ % market
        )
        _ = input()

        # Add the cookies to each ticket
        cookies = self._cookies_content(market)
        while not self._q.empty():
            ticket = self._q.get()
            ticket.value = cookies

        self.lock.release()
        return cookies

    def market(self) -> str | None:
        msg: str = "Introduce the name of the market to crawl"
        prompt = "> "
        log.info(msg)
        market = input(prompt) or None

        return market
