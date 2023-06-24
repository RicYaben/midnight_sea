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
