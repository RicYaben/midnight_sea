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

import yaml
import os
from dataclasses import dataclass, field

from lib.logger.logger import log


@dataclass
class Blueprint:
    """Object to load blueprint information

    Attributes:
        market (str): Name of the market
        model (str): Type of the content

        structure (dict): Instructions to follow to find the content
    """

    market: str
    model: str

    structure: dict = field(default_factory=dict)


def get_blueprint(market: str, model: str) -> Blueprint:
    """Returns a Blueprint object with the data loaded

    Args:
        market (str): Name of the market
        model (str): Type of the content

    Returns:
        Blueprint: Instance of the blueprint
    """
    model = model.lower()
    # Check that the file is there and it is a file
    filename: str = "%s.yaml" % model
    filepath = os.path.join("dist", market, filename)

    if os.path.isfile(filepath):

        # Load the content of the file
        with open(filepath, "r") as file:
            structure = yaml.load(file, yaml.loader.SafeLoader)

            # Load the blueprint and return it
            blueprint = Blueprint(market=market, model=model, structure=structure)
            return blueprint

    else:
        log.error("Blueprint for market %s, model %s not found" % (market, model))
