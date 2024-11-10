from abc import ABC, abstractmethod

from sqlalchemy.orm.session import Session


class IDB(ABC):
    @abstractmethod
    def __enter__(self) -> Session:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, *_) -> None:
        raise NotImplementedError
