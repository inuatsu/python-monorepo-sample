from abc import ABC, abstractmethod

from common.domain.entity.edinet_company import EdinetCompany


class IEdinetCompanyRepository(ABC):
    @abstractmethod
    def get_from_url(self, url: str) -> list[EdinetCompany]:
        raise NotImplementedError

    @abstractmethod
    def save(self, edinet_companies: list[EdinetCompany]) -> None:
        raise NotImplementedError
