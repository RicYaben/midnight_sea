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

from abc import ABC
from typing import Callable
from dataclasses import dataclass


@dataclass
class Service(ABC):
    """Wrapper for the Services"""

    ...


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
