from typing import Any, Callable
from dataclasses import dataclass

@dataclass
class Service:
    name: str

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