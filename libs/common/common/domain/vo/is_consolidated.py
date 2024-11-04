from enum import Enum
from typing import Any

from pydantic import RootModel


class Consolidated(Enum):
    CONSOLIDATED = True
    NON_CONSOLIDATED = False


class IsConsolidated(RootModel[Consolidated]):
    @classmethod
    def from_str(cls, string: Any) -> "IsConsolidated":
        if not isinstance(string, str):
            raise TypeError("Type of argument should be str")
        if string.lower() in ["有", "consolidated", "true"]:
            return IsConsolidated(Consolidated.CONSOLIDATED)
        elif string.lower() in ["無", "non_consolidated", "false"]:
            return IsConsolidated(Consolidated.NON_CONSOLIDATED)
        else:
            raise NotImplementedError
