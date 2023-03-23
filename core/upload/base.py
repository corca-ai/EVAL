from abc import ABC, abstractmethod, abstractstaticmethod

from env import DotEnv

STATIC_DIR = "static"


class AbstractUploader(ABC):
    @abstractmethod
    def upload(self, filepath: str) -> str:
        pass

    @abstractstaticmethod
    def from_settings(settings: DotEnv) -> "AbstractUploader":
        pass
