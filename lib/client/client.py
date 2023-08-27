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

import os
from dataclasses import dataclass, field
from functools import partial
from typing import Any

from lib.logger import logger
from lib.client import ServiceFactory, Service

@dataclass
class Clients:
    client_list: dict[Any, Any] = field(default_factory=dict)
    _certs: str = os.path.join("dist", "certs")

    @property
    def certs(self):
        # NOTE: This is here only for good measure, you should already
        # have the certificates placed in the folder.
        if not os.path.exists(self._certs):
            os.makedirs(self._certs)

        return self._certs

    def build(self, services: dict):
        clients = {}

        # Check if the stubs
        for name, attrs in services.items():

            # Separate the host and the port
            host, port = attrs.values()

            # If there is a host and a port, attempt to get the certificate
            if host and port:
                # cert path
                cert = self.get_cert(name)
                # Load the certificates and send them to the service to can create a stub.
                client = ServiceFactory.get_service(name)
                client = partial(client, host=host, port=port, cert=cert)

            else:
                # Create a local instance of the stub
                client = ServiceFactory.get_service("%s_%s" % ("local", name))

            # Include the stub in the list
            if not client:
                logger.error(f"Client {name} could not be loaded")
                continue

            clients[name] = client()
            logger.info(f"Client {name} loaded...")

        self.client_list = clients
        return self.client_list

    def get_stub(self, service: str) -> Service:
        if service in self.client_list:
            return self.client_list[service]

    def get_cert(self, client: str) -> bytes:
        # cert path
        cert = os.path.join(self.certs, "%s.crt" % client)

        if os.path.isfile(cert):
            with open(cert, "rb") as f:
                return f.read()


def build_clients(services: dict) -> Clients:
    stubs = Clients()
    stubs.build(services)
    return stubs
