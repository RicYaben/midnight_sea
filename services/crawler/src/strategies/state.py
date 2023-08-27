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

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

import yaml


@dataclass
class State:
    """This class aims to provide an interface to store the state
    of the current crawl.
    """

    market: str

    window_max: int = 5
    window_min: int = 2
    markets_folder = os.path.join("dist", "markets")

    _state: Dict[Any, Any] = field(default_factory=dict)
    _state_file: str = ""

    def get_state(self) -> dict:
        market_folder = os.path.join("dist", "markets", self.market)

        # Create the folder if it does not exists yet
        if not os.path.exists(market_folder):
            os.makedirs(market_folder)

        # Create the file if it does not exists
        if not self._state_file:
            self._state_file = os.path.join(market_folder, "state.yaml")
            if not os.path.isfile(self._state_file):
                with open(self._state_file, "w+") as f:
                    yaml.dump(dict(), f)

        # Load the state if there isn't any
        if not self._state:
            with open(self._state_file, "r") as f:
                state = yaml.load(f, yaml.loader.SafeLoader)
                self._state = state or dict()

        return self._state

    def save(self) -> None:
        """Saves the current state to the a file"""
        state = self.get_state()
        with open(self._state_file, "w") as f:
            yaml.dump(state, f)

    def get_status(self, category: str, path: str) -> Dict[Any, Any]:
        """Returns a dictionary containing the current status of some
        page for a given model
        """
        state = self.get_state()

        if not category in state:
            state[category] = []

        cat_stats: list = state[category]
        status = next((x for x in cat_stats if x.get("path") == path), None)

        if not status:
            status = dict(path=path)
            cat_stats.append(status)

        self.save()
        return status

    def calculate_window(self, status: Dict[Any, Any]) -> int:
        """Returns a window integer that can be used  to decide whether some
        category does not contain new items
        """
        if "last_crawl" in status:
            today = datetime.now()
            previous = status.get("last_crawl")

            # Careful with previous dates from the future...
            diff = (today - previous).days

            # I wish I could change this for a CReLu...
            if diff > self.window_max:
                return self.window_max
            elif diff < self.window_min:
                return self.window_min
            else:
                return diff

        else:
            return self.window_max
