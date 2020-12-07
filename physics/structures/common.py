from abc import ABC, abstractmethod


class PhysicsObject(ABC):
    @abstractmethod
    def to_latex(self) -> str:
        pass
