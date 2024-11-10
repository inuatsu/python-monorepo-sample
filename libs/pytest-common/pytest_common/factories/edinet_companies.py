import ulid
from common.models.EdinetCompany import EdinetCompanyOrm
from factory import Faker, Sequence
from factory.alchemy import SQLAlchemyModelFactory


class EdinetCompanyFactory(SQLAlchemyModelFactory):
    class Meta:  # type: ignore
        model = EdinetCompanyOrm

    id = Sequence(lambda _: ulid.new().str.lower())
    edinet_code = Sequence(lambda n: f"E{n:05}")
    submitter_type = "内国法人・組合"
    name = Faker("company", locale="ja_JP")  # type: ignore
