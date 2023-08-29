from dataclasses import dataclass
from lib.config.config import Host
from omegaconf import MISSING

@dataclass
class Database(Host):
    # Username for the database
    username: str = MISSING
    # Password for the database
    password: str = MISSING
    # Name of the database
    db: str = "midnight_sea"
    # Dialect of the db
    dialect: str = "postgresql"
    # Driver
    driver: str = "psycopg2"