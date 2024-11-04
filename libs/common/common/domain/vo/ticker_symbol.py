import string
from typing import Annotated

from pydantic import Field

EXCLUDED_ALPHABETS = ["B", "E", "I", "O", "Q", "V", "Z"]
POSSIBLE_ALPHABETS = "".join([s for s in string.ascii_uppercase if s not in EXCLUDED_ALPHABETS])

TickerSymbol = Annotated[
    str,
    Field(max_length=5, min_length=5, pattern=rf"^\d[\d{POSSIBLE_ALPHABETS}]\d[\d{POSSIBLE_ALPHABETS}]0$", frozen=True),
]
