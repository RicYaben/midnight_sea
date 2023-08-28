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

"""This package contains the Session Handlers to connect to any service"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable

import requests
import tldextract

from crawler.session.budgets import Budget, BudgetFactory, Recommendation
from crawler.session.networks import Network, NetworkFactory

from lib.logger.logger import log

@dataclass
class SessionManager:
    """Wrapper for the requester session

    Attributes:

        TIMEOUT (int): Max. seconds to wait for the server the respond
        _session:   Initialization of the session
    """

    budget: Budget
    cookies_fn: Callable

    cookies: dict[Any, Any] = field(default_factory=dict)
    headers: dict[str, Any] = field(default_factory=lambda: {"user-agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"})

    _timeout: int = 60
    _session: requests.Session = None

    @property
    def session(self) -> requests.Session:
        """Returns the session utilising the proxy given by the network"""
        if not self._session:
            # New session
            session = requests.session()
            self.session = session

        return self._session

    @session.setter
    def session(self, session):
        log.info("Creating new session...")

        # New session
        self._session = session
        self._session.headers.update(**self.headers)

        return self._session

    def get_proxy(self, url: str) -> dict:
        """Returns a dictionary with the proxy"""
        res = tldextract.extract(url)
        
        # [9/17/2022] TODO: This has a bug with I2P urls, where tldextract can not capture i2p suffix.
        prox = "tor" if res.suffix == "onion" else "i2p"
        
        network: Network = NetworkFactory.get_network(prox)()
        return network.get_proxy()

    def request(self, url: str):
        """Returns the list of url's to the new items found in the page
        previous to the last item, if given.

        Args:
            url (str): URL page to request
        """
        recommendation: Recommendation = self.budget.consume()
        delay: float = self.budget.delay
        time.sleep(delay)

        try:
            proxies = self.get_proxy(url)
            log.debug(f"Requesting page: {url}")
            response = self.session.get(
                url, timeout=self._timeout, cookies=self.cookies, proxies=proxies
            )

        except requests.exceptions.RequestException as e:
            response = e.response
            log.error(e)

        if response:
            # Store a health record in the budget
            recommendation.record(
                response,
                self.budget.name,
                response_code=response.status_code,
                url=url,
                elapsed=response.elapsed.seconds,
            )

        return response

    def auth(self, market: str) -> bool:
        """Invoke the `cookies` method from
        a stub object, then, if some cookies have been
        received, set the new cookies in the session.

        Args:
            session (Session): A session object capable of crawling

        Returns:
            bool: Whether the session has been authenticated
        """
        gen_cookies = self.cookies_fn(market)
        cookies = gen_cookies

        # If it returned cookies, we will replace them.
        # The only situation in where we dont get new cookies is when
        # we want to "skip" the page
        if cookies:
            self.cookies = cookies
            return True


def new_session(cookies_fn: Callable, budget: str = "simple") -> SessionManager:
    bd: Budget = BudgetFactory.get_budget(budget)
    budget_instance: Budget= bd()
    return SessionManager(cookies_fn=cookies_fn, budget=budget_instance)
