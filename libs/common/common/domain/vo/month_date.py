import re
from calendar import isleap, monthrange
from datetime import date
from re import Match

from pydantic import BaseModel, computed_field


class MonthDate(BaseModel):
    text: str

    def regex_search(self) -> Match | None:
        text = re.sub(r"\s", "", self.text)
        return re.search(r"(?P<month>\d{,2})[月\-/ー／](?P<date>末|\d{,2})日?", text)

    @computed_field
    @property
    def month(self) -> int | None:
        m = self.regex_search()
        if not m:
            return None
        if not m["month"].isdigit():
            return None
        return int(m["month"])

    @computed_field
    @property
    def date(self) -> int | None:
        m = self.regex_search()
        if not m:
            return None
        if m["date"] == "末":
            this_year = date.today().year
            if not m["month"].isdigit():
                return None
            month = int(m["month"])
            if month == 2:
                return monthrange(this_year, month)[1] - isleap(this_year)
            return monthrange(this_year, month)[1]
        if not m["date"].isdigit():
            return None
        return int(m["date"])
