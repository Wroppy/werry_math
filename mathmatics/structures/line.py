import math
from abc import ABC, abstractmethod

from mathmatics.geometry.equation import LinearEquation
from mathmatics.structures.common import MathObject
from mathmatics.structures.equation import Equation
from mathmatics.structures.vector import Vector2D


class Line(MathObject, ABC):

    @abstractmethod
    def magnitude(self) -> float:
        pass

    @abstractmethod
    def to_equation(self) -> Equation:
        pass

    @abstractmethod
    def __str__(self):
        pass


class Line2D(Line):
    def __init__(self, start: Vector2D, end: Vector2D):
        self.start = start
        self.end = end

    def magnitude(self) -> float:
        return math.sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2)

    def slope(self) -> float:
        return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def mid_point(self) -> Vector2D:
        return Vector2D((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)

    def y_intercept(self) -> float:
        return self.start.y - (self.slope() * self.start.x)

    def to_equation(self) -> LinearEquation:
        return LinearEquation(self.slope(), self.y_intercept())

    def to_latex(self) -> str:
        return f"(({self.start.x}, {self.start.y}), ({self.end.x}, {self.end.y}))"

    def __str__(self):
        return f"Line start: ({self.start.x}, {self.start.y}), end: ({self.end.x}, {self.end.y})"


if __name__ == '__main__':
    line = Line2D(Vector2D(1, 2), Vector2D(5, 7))
    print(line.mid_point())
    print(line.y_intercept())
    # line.to_equation().graph()
    line.open_in_desmos()