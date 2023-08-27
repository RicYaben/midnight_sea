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

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Plan:
    """Wrapper for the plans gotten from the planner.
    It contains important market features and how to validate
    the pages.

    Attributes:
        data (Dict[Any, Any]): Object returned from the planner. The plan itself.
    """

    data: Dict[Any, Any] = field(default_factory=dict)

    def section(self, model: str, name: str, all: bool = True) -> Dict[Any, Any]:
        """Returns the list of values found in the given section"""
        models: dict = self.data.get("models")
        search: list = [model]

        if all:
            search.append("all")

        ret = {}

        for m, v in models.items():
            if m in search and name in v:
                section = v.get(name)
                ret[m] = section

        return ret
