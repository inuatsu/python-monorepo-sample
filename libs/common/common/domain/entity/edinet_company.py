from pydantic import BaseModel, Field, computed_field

from common.domain.vo.capital_stock import CapitalStock
from common.domain.vo.corporate_number import CorporateNumber
from common.domain.vo.edinet_code import EdinetCode
from common.domain.vo.industry import Industry
from common.domain.vo.is_consolidated import IsConsolidated
from common.domain.vo.is_listed import IsListed
from common.domain.vo.month_date import MonthDate
from common.domain.vo.ticker_symbol import TickerSymbol


class EdinetCompany(BaseModel):
    edinet_code: EdinetCode
    submitter_type: str
    is_listed: IsListed | None = Field(default=None)
    is_consolidated: IsConsolidated | None = Field(default=None)
    capital_stock: CapitalStock | None = Field(default=None)
    account_closing_month_date: MonthDate | None = Field(default=None, exclude=True)
    name: str
    english_name: str | None = Field(default=None)
    name_kana: str | None = Field(default=None)
    address: str | None = Field(default=None)
    industry: Industry | None = Field(default=None)
    ticker_symbol: TickerSymbol | None = Field(default=None)
    corporate_number: CorporateNumber | None = Field(default=None)

    @computed_field
    @property
    def account_closing_month(self) -> int | None:
        if self.account_closing_month_date:
            return self.account_closing_month_date.month
        return None

    @computed_field
    @property
    def account_closing_date(self) -> int | None:
        if self.account_closing_month_date:
            return self.account_closing_month_date.date
        return None
