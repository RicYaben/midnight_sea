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

import time
from dataclasses import dataclass
from queue import Queue
from typing import Any, Callable, Dict, Protocol, Sequence

import grpc
from ms_crawler.globals import logger
from ms_crawler.strategies.content import Page


class Core(Protocol):
    """Protocol for the Core Service"""

    class Ticket:
        value: Any = None

    name: str = "core"
    _q: Queue = Queue()
    _locked: bool = False

    def wait(self, ticket: Ticket):
        logger.debug("Waiting to unlock...")
        while not ticket.value:
            time.sleep(2)

        return ticket.value

    @property
    def locked(self):
        return self._locked

    def lock(self):
        self._locked = True

    def unlock(self, value: Any):
        while not self._q.empty():
            ticket = self._q.get()
            ticket.value = value

        self._locked = False

    def cookies(self, market: str) -> Dict[Any, Any]:
        ...

    def market(self) -> str | None:
        ...


class Storage(Protocol):
    """Storage Protocol"""

    name: str = "storage"

    def store(self, pages: Sequence[Page], market: str, model: str) -> bool:
        ...

    def pending(self, market: str, model: str) -> Sequence[Dict[Any, Any]]:
        ...

    def check(self, market: str, model: str, pages: Sequence[str]) -> Sequence[Page]:
        ...


class Planner(Protocol):
    """Planner Protocol"""

    name: str = "planner"

    def plan(self, market: str) -> Dict[Any, Any]:
        ...


@dataclass
class Service:
    name: str = None


class ExService(Service):
    """Interface to connect to a given external service"""

    channel: grpc.Channel = None
    stub = None

    _stub_class = None

    def __init__(self, host: str, port: int, cert: bytes) -> None:
        # Make a secure channel if there is a certificate, otherwise create an insecure channel.
        if cert:
            credentials = grpc.ssl_channel_credentials(cert)
            self.channel = grpc.secure_channel(
                "%s:%s" % (host, port), credentials=credentials
            )
        else:
            self.channel = grpc.insecure_channel("%s:%s" % (host, port))
            logger.warning(f"Loaded service using insecure channel on {host}:{port}")

        self.stub = self._stub_class(self.channel)


@dataclass
class ServiceFactory:
    services = {}

    @classmethod
    def get_service(cls, service: str) -> Service:
        if service in cls.services:
            return cls.services[service]

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Service) -> Service:
            cls.services[name] = decorator_cls

            return decorator_cls

        return decorator
