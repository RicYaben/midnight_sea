import os
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Dict

from ms_crawler.client.interfaces import Service, ServiceFactory

# Necessary Imports for the "ServiceFactory" to register the services
from ms_crawler.client.services import core, planner, storage
from ms_crawler.globals import CERTS, SERVICES, logger


@dataclass
class Stubs:
    stubs: Dict[Any, Any] = field(default_factory=dict)
    _certs: str = os.path.join(CERTS, "clients")

    @property
    def certs(self):
        # NOTE: This is here only for good measure, you should already
        # have the certificates placed in the folder.
        if not os.path.exists(self._certs):
            os.makedirs(self._certs)

        return self._certs

    def build(self, services: dict):
        stubs = {}

        # Check if the stubs
        for service, attrs in services.items():

            logger.debug(f"Loading {service} service...")

            # Separate the host and the port
            host, port = attrs.values()

            # If there is a host and a port, attempt to get the certificate
            if host and port:
                # cert path
                cert = self.get_cert(service)
                # Load the certificates and send them to the service to can create a stub.
                client = ServiceFactory.get_service(service)
                client = partial(client, host=host, port=port, cert=cert)

            else:
                # Create a local instance of the stub
                client = ServiceFactory.get_service("%s_%s" % ("local", service))

            # Include the stub in the list
            if client:
                stubs[service] = client()
                logger.info(f"{service} service loaded...")

        self.stubs = stubs
        return self.stubs

    def get_stub(self, service: str) -> Service:
        if service in self.stubs:
            return self.stubs[service]

    def get_cert(self, client: str) -> bytes:
        # cert path
        cert = os.path.join(self.certs, "%s.crt" % client)

        if os.path.isfile(cert):
            with open(cert, "rb") as f:
                return f.read()


def build_stubs() -> Stubs:
    stubs = Stubs()
    stubs.build(SERVICES)
    return stubs
