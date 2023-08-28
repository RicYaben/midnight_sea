from typing import Callable

from lib.stubs.interfaces import Stub
from lib.conf.config import Client

import os
import grpc

class StubFactory:
    stubs: dict[str, Stub] = {}
    local_stubs: dict[str, Stub] = {}

    @classmethod
    def get_stub(cls, name: str, local: bool=False):
        stub_dict = cls.local_stubs if local else cls.stubs
        if name in stub_dict:
            ret = stub_dict[name]
            return ret

    @classmethod
    def register(cls, name: str, local: bool=False) -> Callable:
        def decorator(decorator_cls: Client) -> Client:
            if local:
                cls.local_stubs[name] = decorator_cls
            else:
                cls.stubs[name] = decorator_cls

            return decorator_cls

        return decorator
    
    @classmethod
    def create_stub(cls, client: Client) -> Stub | None:
        stub: Stub = cls.get_stub(client.name, client.local)
        if not stub:
            return None

        cert_path = os.path.join("dist/certs", "%s.crt" % client.name)
        if os.path.isfile(cert_path):
            with open(cert_path, "rb") as f:
                cert = f.read()
                creds = grpc.ssl_channel_credentials(cert)

                channel = grpc.secure_channel(
                    "%s:%s" % (client.address, client.port), credentials=creds
                )
            
        else:
            channel = grpc.insecure_channel("%s:%s" % (client.address, client.port))

        return stub(client= client, channel= channel)