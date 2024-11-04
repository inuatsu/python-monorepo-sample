from enum import Enum
from typing import Any

from pydantic import RootModel


class Listed(Enum):
    LISTED = True
    UNLISTED = False


class IsListed(RootModel[Listed]):
    @classmethod
    def from_str(cls, string: Any) -> "IsListed":
        if not isinstance(string, str):
            raise TypeError("Type of argument should be str")
        if string.lower() in ["上場", "listed", "true"]:
            return IsListed(Listed.LISTED)
        elif string.lower() in ["非上場", "unlisted", "false"]:
            return IsListed(Listed.UNLISTED)
        else:
            raise NotImplementedError
