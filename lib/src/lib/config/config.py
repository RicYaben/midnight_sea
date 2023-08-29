from dataclasses import dataclass, field
from omegaconf import MISSING

import logging

@dataclass
class Host:
    # Name of the host
    name: str = MISSING
    # Host in where it can be reached
    address: str = "localhost"
    # Listening port
    port: int = 80

@dataclass
class Client(Host):
    # Whether to load the local version
    local: bool = False

@dataclass
class Config:
    host: Host = MISSING
    # Log
    verbose: int = logging.DEBUG
    # Communication
    clients: dict[str, Client] = field(default_factory=dict)