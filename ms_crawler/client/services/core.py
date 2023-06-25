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

import json
import os

from typing import Any, Dict

# from pytimedinput import timedInput
from google.protobuf import message, json_format


from ms_crawler.globals import VOLUME, logger, SERVICE_ID
from ms_crawler.client.interfaces import (
    Core,
    ExService,
    Service,
    ServiceFactory,
)

from ms_crawler.protos.crawler_pb2_grpc import CrawlerStub
from ms_crawler.protos.crawler_pb2 import CookiesRequest, MarketRequest


@ServiceFactory.register("core")
class CoreService(ExService, Core):
    _stub_class = CrawlerStub
    _timeout: int = 600  # 10 min

    def __init__(self, host: str, port: int, cert: bytes) -> None:
        super().__init__(host, port, cert)

    def cookies(self, market: str) -> Dict[Any, Any]:
        if self.locked:
            ticket = self.Ticket()
            self._q.put(ticket)
            return self.wait(ticket)

        # Lock the service
        self.lock()
        logger.info("Requesting new cookies, this might need attention!")

        # Request for cookies to the stub
        request = CookiesRequest(market=market)
        response = self.stub.GetCookies(request, timeout=self._timeout)
        cookies: message = response.cookies
        ret = json_format.MessageToDict(cookies)

        # Unlock the service
        self.unlock(ret)
        logger.info("Resumming...")

        return ret

    def market(self) -> str | None:
        """Request the market to the stub"""
        logger.info("Requesting Market...")

        # Get the market once
        req = MarketRequest(stub=SERVICE_ID)
        response = self.stub.WaitForMarket(req, timeout=self._timeout)

        # Send back the response
        return response.market


@ServiceFactory.register("local_core")
class LocalCoreService(Service, Core):
    """Local Core Service.

    Interacts with the host shell to prompt for the market and cookies
    """

    TIMEOUT = 30  # Seconds
    FILENAME: str = "cookies.json"

    def _cookies_content(self, market):
        """Returns the content of the cookies file"""
        folder = os.path.join(VOLUME, "markets", market)

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

    def _continue(self) -> bool:
        skip = "skip"
        logger.warning(
            "When you are ready, introduce any value. If you rather skip this link, introduce `skip`"
        )

        # prompt for input
        prompt: str = "[Any|%s]: " % skip
        # [4/2/2022] NOTE: we are removing the timeout to lock the flow. Sometimes you might
        # need a lot of time in between.
        # cont, _ = timedInput(prompt, timeout=self.TIMEOUT)
        cont = input(prompt) or None

        if cont == skip:
            return False

        # If it times out, returns True
        return True

    def cookies(self, market: str) -> Dict[Any, Any]:
        """Builds cookies from a given file"""

        # If the service is locked, grant a ticket
        if self.locked:
            ticket = self.Ticket()
            self._q.put(ticket)
            return self.wait(ticket)

        # Lock the service
        self.lock()

        msg: str = "Market %s needs authentication" % (market)
        logger.warning(msg)

        # NOTE: We prompt so we can stop the application for a few moments
        # and place the cookies
        cont = self._continue()
        cookies = {}

        if cont:
            # Get the cookies
            self.unlock(cookies)
            cookies = self._cookies_content(market)

            logger.info("Resumming...")
            return cookies

    def market(self) -> str | None:
        msg: str = "Introduce the name of the market to crawl"
        prompt = "> "
        logger.info(msg)
        market = input(prompt) or None

        return market
