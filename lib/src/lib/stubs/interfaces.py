from dataclasses import dataclass, field
from typing import Protocol, Any
from grpc import Channel
from lib.config.config import Client

class LocalStubCls:
    def __init__(self, *args, **kwargs) -> None:
        return

@dataclass
class Stub(Protocol):
    """
    This abstract stub is meant to be used as the base for other stubs.
    The only functionality it implements is 
    """
    # Host where the stub is located
    client: Client
    # Instance of the stub
    stub: Any
    # Class to load the stub (given from GRPC)
    _stub_cls: Any = field(init=False, repr=False)

    @classmethod
    def create(cls, client: Client, channel: Channel):
        stub = cls._stub_cls(channel)
        return cls(client=client, stub=stub)