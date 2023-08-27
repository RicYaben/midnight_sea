from dataclasses import dataclass, field

import logging

@dataclass
class Host:
    # Name of the host
    name: str
    # Host in where it can be reached
    address: str = field(default_factory=None)
    # Listening port
    port: int = field(default_factory=None)
    

@dataclass
class Client(Host):
    # Whether to load the local version
    local: bool = False

@dataclass
class Config:
    host: Host
    # Log
    verbose: int = logging.DEBUG
    # Paths
    resources: str = "resources"
    # Communication
    clients: [Client] = field(default_factory=list)