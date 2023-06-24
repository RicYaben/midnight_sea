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
