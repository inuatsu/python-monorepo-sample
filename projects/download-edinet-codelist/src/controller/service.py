from abc import ABC, abstractmethod


class IDownloadEdinetCodelistUsecase(ABC):
    @abstractmethod
    def handle(self) -> None:
        raise NotImplementedError
