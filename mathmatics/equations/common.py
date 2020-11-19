from abc import ABC, abstractmethod

from mathmatics.geometry.quadratic import solve_quadratic
from mathmatics.structures.vector import Vector2D


class Equation(ABC):
    @abstractmethod
    def y(self, x: float) -> float:
        pass

    def print_y(self, x: float):
        print(self.y(x))


if __name__ == '__main__':
    eq = Equation()
    print(eq)
