import ulid
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

on_create = text("CURRENT_TIMESTAMP")
on_update = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


def generate_ulid() -> str:
    return ulid.new().str.lower()


class Base(DeclarativeBase):
    pass
