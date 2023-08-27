import os
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    service: str = None

    host: str = "localhost"
    port: int = 0

    # Log
    verbose: str = "DEBUG"

    # Paths
    resources: str = "resources"

    # Communication
    allowedServices: [(str, int)] = []

    
