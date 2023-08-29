import os

from typing import Callable

from lib.stubs.interfaces import Stub, LocalStubCls
from lib.config.config import Client
from lib.logger.logger import log

from grpc import Channel, insecure_channel, secure_channel, ssl_channel_credentials


class StubNotFoundException(Exception):
    pass

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
            raise StubNotFoundException
        
        channel: Channel = None
        if not client.local:
            cert_path = os.path.join("dist/certs", "%s.crt" % client.name)
            if os.path.isfile(cert_path):
                with open(cert_path, "rb") as f:
                    cert = f.read()
                    creds = ssl_channel_credentials(cert)

                    channel: Channel = secure_channel(
                        "%s:%s" % (client.address, client.port), credentials=creds
                    )
                
            else:
                channel: Channel = insecure_channel("%s:%s" % (client.address, client.port))
                log.info("Created insecure channel with %s" % client.name)

        instance = stub.create(client=client, channel=channel)
        return instance