from typing import Union

from mathmatics.geometry.quadratic import solve_quadratic
from mathmatics.structures.equation import Equation
from mathmatics.structures.vector import Vector2D


class ExponentialEquation(Equation):

    def __init__(self, a: float, b: float, c: float = 0):
        self.a = a
        self.b = b
        self.c = c

    def y(self, x: float) -> float:
        return self.a * self.b ** x + self.c

    def to_latex(self) -> Union[str, None]:
        return f"{self.a}*{self.b}^x+{self.c}"


class QuadraticEquation(Equation):
    def __init__(self, a: float, b: float, c: float = 0):
        self.a = a
        self.b = b
        self.c = c

    def y(self, x: float) -> float:
        return self.a * x ** 2 + self.b * x + self.c

    def x_intercepts(self) -> Vector2D:
        return solve_quadratic(self.a, self.b, self.c)

    def to_latex(self) -> Union[str, None]:
        return f"{self.a}*x^2+{self.b}*x+{self.c}"


class LinearEquation(Equation):
    def __init__(self, m: float, c: float):
        self.m = m
        self.c = c

    def y(self, x: float) -> float:
        return self.m * x + self.c

    def to_latex(self) -> Union[str, None]:
        return f"{self.m}*x+{self.c}"


if __name__ == '__main__':
    eq = ExponentialEquation(1, 15)
    eq.open_in_desmos()