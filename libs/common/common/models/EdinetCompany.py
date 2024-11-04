from datetime import datetime

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from common.models.Base import Base, generate_ulid, on_create, on_update


class EdinetCompanyOrm(Base):
    __tablename__ = "edinet_companies"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=generate_ulid)
    edinet_code: Mapped[str] = mapped_column(String(6), unique=True)
    submitter_type: Mapped[str] = mapped_column(String(50))
    is_listed: Mapped[bool | None]
    is_consolidated: Mapped[bool | None]
    capital_stock: Mapped[int | None] = mapped_column(BigInteger)
    account_closing_month: Mapped[int | None]
    account_closing_date: Mapped[int | None]
    name: Mapped[str] = mapped_column(String(150))
    english_name: Mapped[str | None] = mapped_column(String(600))
    name_kana: Mapped[str | None] = mapped_column(String(500))
    address: Mapped[str | None] = mapped_column(String(300))
    industry: Mapped[str | None] = mapped_column(String(100))
    ticker_symbol: Mapped[str | None] = mapped_column(String(5))
    corporate_number: Mapped[str | None] = mapped_column(String(13))
    created_at: Mapped[datetime] = mapped_column(server_default=on_create)
    updated_at: Mapped[datetime] = mapped_column(server_default=on_update)
