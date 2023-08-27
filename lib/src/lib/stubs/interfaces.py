from dataclasses import dataclass
from typing import Protocol, Any
from grpc import Channel
from lib.conf.config import Client

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
    # Channel to communicate with the stub
    channel: Channel
    # Instance of the stub
    _stub: Any = None
    # Class to load the stub (given from GRPC)
    _stub_cls: Any = LocalStubCls

    @property
    def stub(self) -> Any:
        return self._stub

    def __post_init__(self) -> None:
        self._stub = self._stub_cls(self.channel)
        
