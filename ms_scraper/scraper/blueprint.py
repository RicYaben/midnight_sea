import yaml
import os
from dataclasses import dataclass, field

from ms_scraper.globals import BLUEPRINTS, logger


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
    filepath = os.path.join(BLUEPRINTS, market, filename)

    if os.path.isfile(filepath):

        # Load the content of the file
        with open(filepath, "r") as file:
            structure = yaml.load(file, yaml.loader.SafeLoader)

            # Load the blueprint and return it
            blueprint = Blueprint(market=market, model=model, structure=structure)
            return blueprint

    else:
        logger.error("Blueprint for market %s, model %s not found" % (market, model))
