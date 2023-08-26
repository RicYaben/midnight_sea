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

from dataclasses import dataclass
from typing import Callable, Protocol

import grpc


class Scraper(Protocol):
    def scrape(self, model: str, market: str, data: bytes):
        raise NotImplementedError


class ExService:
    """Interface to connect to a given external service"""

    channel: grpc.Channel = None
    stub = None

    _stub_class = None

    def __init__(self, host: str, port: int, cert: bytes) -> None:
        # Make a secure channel
        if cert:
            credentials = grpc.ssl_channel_credentials(cert)
            self.channel = grpc.secure_channel(
                "%s:%s" % (host, port), credentials=credentials
            )
        else:
            self.channel = grpc.insecure_channel("%s:%s" % (host, port))

        self.stub = self._stub_class(self.channel)


@dataclass
class ServiceFactory:
    services = {}

    @classmethod
    def get_service(cls, service: str):
        if service in cls.services:
            return cls.services[service]

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls):
            cls.services[name] = decorator_cls

            return decorator_cls

        return decorator
