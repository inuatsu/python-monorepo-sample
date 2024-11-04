from typing import Annotated

from pydantic import Field

EdinetCode = Annotated[str, Field(max_length=6, min_length=6, pattern=r"^E\d{5}$", frozen=True)]
