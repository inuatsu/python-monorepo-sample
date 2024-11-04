from typing import Any

from pydantic import RootModel


class CapitalStock(RootModel[int]):
    @classmethod
    def to_int(cls, value: Any) -> "CapitalStock":
        if isinstance(value, str):
            return CapitalStock(int(value.replace(",", "")))
        elif isinstance(value, int):
            return CapitalStock(value)
        else:
            raise TypeError("Type of argument should be str or int")
