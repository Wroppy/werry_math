from mathmatics.equations.common import Equation
from mathmatics.geometry.quadratic import solve_quadratic
from mathmatics.structures.vector import Vector2D


class ExponentialEquation(Equation):
    def __init__(self, a: float, b: float, c: float = 0):
        self.a = a
        self.b = b
        self.c = c

    def y(self, x: float) -> float:
        return self.a * self.b ** x + self.c

    def __str__(self):
        return f"y = {self.a}*{self.b}^x+{self.c}"


class QuadraticEquation(Equation):
    def __init__(self, a: float, b: float, c: float = 0):
        self.a = a
        self.b = b
        self.c = c

    def y(self, x: float) -> float:
        return self.a * x ** 2 + self.b * x + self.c

    def x_intercepts(self) -> Vector2D:
        return solve_quadratic(self.a, self.b, self.c)

    def __str__(self):
        return f"y = {self.a}*x^2+{self.b}*x+{self.c}"

