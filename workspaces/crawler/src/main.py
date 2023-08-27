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

"""
Main entrypoint for the application
"""

from lib.conf.config import ServiceConfig
from crawler.flags import parse_flags

import hydra
from hydra.core.config_store import ConfigStore

cs = ConfigStore.instance()
# Registering the Config class with the name 'config'.
cs.store(name="config", node=ServiceConfig)

@hydra.main(version_base=None, config_name="config")
def main(cfg: ServiceConfig):
    parse_flags(cfg)

if __name__ == "__main__":
    main()
