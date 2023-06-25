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
from typing import Any, Callable, Dict, Protocol

from ms_crawler.globals import PROXY_HOST


@dataclass
class Network(Protocol):
    protocol: str
    port: int
    host: str = PROXY_HOST

    def get_proxy(self) -> Dict[Any, Any]:
        """Generic build a proxy for http and https redirections"""
        url: str = "%s://%s:%d" % (self.protocol, self.host, self.port)
        ret: dict = dict(http=url, https=url)
        return ret

    def as_str(self) -> str:
        url: str = "%s://%s:%d" % (self.protocol, self.host, self.port)
        return url


@dataclass
class NetworkFactory:
    networks = {}

    @classmethod
    def get_network(cls, network: str) -> Network:
        if network in cls.networks:
            return cls.networks[network]

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Network) -> Network:
            cls.networks[name] = decorator_cls

            return decorator_cls

        return decorator


@NetworkFactory.register("tor")
class Tor(Network):
    protocol: str = "socks5h"  # Use Socks5 for both http and https
    port: int = 9050  # 9050


@NetworkFactory.register("i2p")
class I2P(Network):
    protocol: str = "http"
    port: int = 4444  # 4444
