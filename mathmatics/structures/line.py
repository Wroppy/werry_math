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
    def to_ray(self) -> 'Ray':
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

    def to_ray(self) -> 'Ray':
        return Ray2D(self.magnitude(), self.y_intercept())

    def __str__(self):
        return f"Line start: ({self.start.x}, {self.start.y}), end: ({self.end.x}, {self.end.y})"



class Ray(MathObject, ABC):
    @abstractmethod
    def to_equation(self) -> Equation:
        pass

    @abstractmethod
    def to_line(self) -> 'Line':
        pass

    @abstractmethod
    def y(self, x: float) -> float:
        pass


class Ray2D(Ray):
    def to_latex(self) -> str:
        return f"{self.m}*x+{self.c}"

    def __init__(self, m: float, c: float):
        self.m = m
        self.c = c

    def to_equation(self) -> Equation:
        return LinearEquation(self.m, self.c)

    def to_line(self) -> 'Line':
        return Line2D(Vector2D(0, self.c), Vector2D(1, self.m))

    def y(self, x: float) -> float:
        return self.m * x + self.c

    @staticmethod
    def from_gradient_and_sample(m: float, sample: Vector2D) -> 'Ray2D':
        c = sample.y - m * sample.x
        return Ray2D(m, c)

if __name__ == '__main__':


    # line.to_equation().graph()
    pass