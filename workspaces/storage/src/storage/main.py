#!/usr/bin/python3
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

"""Generic entry point to start for DNM Storage"""

import sys
import multiprocessing
from dataclasses import dataclass

from storage.database.database import create_database

from lib.server.factory import ServerFactory, start_server
from lib.config.config import Config
from storage.database.interfaces import Database

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import MISSING
from storage.server.storage import Storage


@dataclass
class StorageConfig(Config):
    # Database configuration
    db: Database = MISSING


cs = ConfigStore.instance()
# Registering the Config class with the name 'config'.
cs.store(name="base_config", node=StorageConfig)

@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: Config) -> None:
    # Read the credentials and build the server
    server = ServerFactory.create_server(servicer=Storage, host=cfg.host, workers=10)
    # Create a database connection and load the models
    _ = create_database(cfg.db)

    start_server(server)

if __name__ == "__main__":
    sys.exit(main())
