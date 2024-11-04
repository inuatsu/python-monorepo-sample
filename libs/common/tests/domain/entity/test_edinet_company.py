from typing import NamedTuple

from pydantic import ValidationError
from pytest import mark, raises

from common.domain.entity.edinet_company import EdinetCompany
from common.domain.vo.capital_stock import CapitalStock
from common.domain.vo.industry import Industry
from common.domain.vo.is_consolidated import IsConsolidated
from common.domain.vo.is_listed import IsListed
from common.domain.vo.month_date import MonthDate


class EdinetCompanyParam(NamedTuple):
    edinet_code: str
    submitter_type: str
    is_listed: IsListed | None
    is_consolidated: IsConsolidated | None
    capital_stock: CapitalStock | None
    account_closing_month_date: MonthDate | None
    name: str
    english_name: str | None
    name_kana: str | None
    address: str | None
    industry: Industry | None
    ticker_symbol: str | None
    corporate_number: str | None


class InvalidIsListedParam(NamedTuple):
    exception_class: type[BaseException]
    exception_message: str
    is_listed: str | list[str]


class InvalidIsConsolidatedParam(NamedTuple):
    exception_class: type[BaseException]
    exception_message: str
    is_consolidated: str | list[str]


class InvalidCorporateNumberParam(NamedTuple):
    exception_class: type[BaseException]
    exception_message: str
    corporate_number: str


class TestEdinetCompany:
    valid_edinet_company_params = [
        EdinetCompanyParam(
            edinet_code="E00001",
            submitter_type="内国法人・組合",
            is_listed=IsListed.from_str("上場"),
            is_consolidated=IsConsolidated.from_str("有"),
            capital_stock=CapitalStock.to_int(1000),
            account_closing_month_date=MonthDate(text="12月31日"),
            name="サンプル株式会社",
            english_name="Sample Co., Ltd.",
            name_kana="サンプルカブシキガイシャ",
            address="東京都千代田区千代田１−１",
            industry=Industry.from_str("水産・農林業"),
            ticker_symbol="11110",
            corporate_number="7010001000000",
        ),
        EdinetCompanyParam(
            edinet_code="E00009",
            submitter_type="内国法人・組合（有価証券報告書等の提出義務者以外）",
            is_listed=IsListed.from_str("非上場"),
            is_consolidated=IsConsolidated.from_str("有"),
            capital_stock=CapitalStock.to_int("1000"),
            account_closing_month_date=MonthDate(text="10 月末日"),
            name="株式会社テスト",
            english_name="Test Co., Ltd.",
            name_kana="カブシキガイシャテスト",
            address="東京都千代田区千代田１−１",
            industry=Industry.from_str("情報・通信業"),
            ticker_symbol=None,
            corporate_number="010001000001",
        ),
        EdinetCompanyParam(
            edinet_code="E10001",
            submitter_type="外国法人・組合",
            is_listed=IsListed.from_str("非上場"),
            is_consolidated=IsConsolidated.from_str("無"),
            capital_stock=CapitalStock.to_int("1,000"),
            account_closing_month_date=MonthDate(text="2月末日"),
            name="テスト株式会社",
            english_name="Test Co., Ltd.",
            name_kana="テストカブシキガイシャ",
            address="東京都千代田区千代田１−１",
            industry=Industry.from_str("外国法人・組合"),
            ticker_symbol=None,
            corporate_number="2700150000000",
        ),
        EdinetCompanyParam(
            edinet_code="E20001",
            submitter_type="個人（組合発行者を除く）",
            is_listed=None,
            is_consolidated=None,
            capital_stock=CapitalStock.to_int("0"),
            account_closing_month_date=None,
            name="田中　太郎",
            english_name=None,
            name_kana="タナカ　タロウ",
            address=None,
            industry=Industry.from_str("個人（組合発行者を除く）"),
            ticker_symbol=None,
            corporate_number=None,
        ),
    ]

    @mark.parametrize("param", valid_edinet_company_params)
    def test_valid(self, param: EdinetCompanyParam, snapshot):
        assert (
            EdinetCompany(
                edinet_code=param.edinet_code,
                submitter_type=param.submitter_type,
                is_listed=param.is_listed,
                is_consolidated=param.is_consolidated,
                capital_stock=param.capital_stock,
                account_closing_month_date=param.account_closing_month_date,
                name=param.name,
                english_name=param.english_name,
                name_kana=param.name_kana,
                address=param.address,
                industry=param.industry,
                ticker_symbol=param.ticker_symbol,
                corporate_number=param.corporate_number,
            )
            == snapshot
        )

    def test_invalid_edinet_code(self):
        with raises(ValidationError):
            EdinetCompany(edinet_code="A00001", submitter_type="内国法人・組合", name="テスト株式会社")

    invalid_is_listed_params = [
        InvalidIsListedParam(
            exception_class=TypeError, exception_message="Type of argument should be str", is_listed=["テスト"]
        ),
        InvalidIsListedParam(exception_class=NotImplementedError, exception_message="", is_listed="テスト"),
    ]

    @mark.parametrize("param", invalid_is_listed_params)
    def test_invalid_is_listed(self, param: InvalidIsListedParam):
        with raises(param.exception_class, match=param.exception_message):
            EdinetCompany(
                edinet_code="E00001",
                submitter_type="内国法人・組合",
                is_listed=IsListed.from_str(param.is_listed),
                name="テスト株式会社",
            )

    invalid_is_consolidated_params = [
        InvalidIsConsolidatedParam(
            exception_class=TypeError, exception_message="Type of argument should be str", is_consolidated=["テスト"]
        ),
        InvalidIsConsolidatedParam(exception_class=NotImplementedError, exception_message="", is_consolidated="テスト"),
    ]

    @mark.parametrize("param", invalid_is_consolidated_params)
    def test_invalid_is_consolidated(self, param: InvalidIsConsolidatedParam):
        with raises(param.exception_class, match=param.exception_message):
            EdinetCompany(
                edinet_code="E00001",
                submitter_type="内国法人・組合",
                is_consolidated=IsConsolidated.from_str(param.is_consolidated),
                name="テスト株式会社",
            )

    def test_invalid_capital_stock(self):
        with raises(TypeError, match="Type of argument should be str or int"):
            EdinetCompany(
                edinet_code="E00001",
                submitter_type="内国法人・組合",
                capital_stock=CapitalStock.to_int(150.5),
                name="テスト株式会社",
            )

    @mark.parametrize("month_date_text", [("八月三十一日"), ("テスト"), ("二月末日")])
    def test_invalid_account_closing_date(self, month_date_text: str, snapshot):
        assert (
            EdinetCompany(
                edinet_code="E00001",
                submitter_type="内国法人・組合",
                account_closing_month_date=MonthDate(text=month_date_text),
                name="テスト株式会社",
            )
            == snapshot
        )

    def test_invalid_industry(self):
        with raises(TypeError, match="Type of argument should be str"):
            EdinetCompany(
                edinet_code="E00001",
                submitter_type="内国法人・組合",
                name="テスト株式会社",
                industry=Industry.from_str(1),
            )

    def test_invalid_ticker_symbol(self):
        with raises(ValidationError):
            EdinetCompany(
                edinet_code="E00001", submitter_type="内国法人・組合", name="テスト株式会社", ticker_symbol="GOOGL"
            )

    invalid_corporate_number_params = [
        InvalidCorporateNumberParam(
            exception_class=TypeError, exception_message="Type of value should be str", corporate_number=1234567890123
        ),
        InvalidCorporateNumberParam(
            exception_class=ValueError, exception_message="Value should be digit", corporate_number="1234567890abc"
        ),
        InvalidCorporateNumberParam(
            exception_class=ValueError,
            exception_message="Length of given value should be 12 or 13",
            corporate_number="12345678901",
        ),
        InvalidCorporateNumberParam(
            exception_class=ValueError,
            exception_message="Length of given value should be 12 or 13",
            corporate_number="12345678901234",
        ),
        InvalidCorporateNumberParam(
            exception_class=ValueError,
            exception_message="Given value is not valid corporate number",
            corporate_number="1234567890123",
        ),
    ]

    @mark.parametrize("params", invalid_corporate_number_params)
    def test_invalid_corporate_number(self, params: InvalidCorporateNumberParam):
        with raises(params.exception_class, match=params.exception_message):
            EdinetCompany(
                edinet_code="E00001",
                submitter_type="内国法人・組合",
                name="テスト株式会社",
                corporate_number=params.corporate_number,
            )
