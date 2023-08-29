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

from queue import Queue
from typing import Any
from dataclasses import dataclass

from lib.stubs.interfaces import Stub

from crawler.strategies.page import Page

from threading import Lock

@dataclass
class Core(Stub):
    """Protocol for the Core Service"""

    class Ticket:
        value: Any = None

    name: str = "core"
    lock = Lock()

    _q: Queue = Queue()

    @property
    def locked(self):
        return self._locked

    def add_ticket(self, ticket: Ticket):
        self._q.put(ticket)

    def unlock(self, value: Any):
        while not self._q.empty():
            ticket = self._q.get()
            ticket.value = value

    def cookies(self, market: str) -> dict[Any, Any]:
        raise NotImplementedError

    def market(self) -> str | None:
        raise NotImplementedError

@dataclass
class Storage(Stub):
    """Storage Protocol"""

    def store(self, pages: list[Page], market: str, model: str) -> bool:
        raise NotImplementedError

    def pending(self, market: str, model: str) -> list[dict[Any, Any]]:
        raise NotImplementedError

    def check(self, market: str, model: str, pages: list[str]) -> list[Page]:
        raise NotImplementedError

@dataclass
class Planner(Stub):
    """Planner Protocol"""

    def get_plan(self, market: str) -> dict[Any, Any]:
        raise NotImplementedError