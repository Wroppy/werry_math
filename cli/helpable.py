from abc import ABC, abstractmethod


class Helpable(ABC):
    help_key: str = 'help'

    @abstractmethod
    def help_for(self, key: str) -> str:
        pass

    @abstractmethod
    def help(self) -> str:
        pass

    @abstractmethod
    def contains_key(self, key) -> bool:
        pass