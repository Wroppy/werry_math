class Equation:
    def y(self, x: float) -> float:
        pass


class ExponentialEquation(Equation):
    def __init__(self, a: float, b: float, c: float = 0):
        self.a = a
        self.b = b
        self.c = c

    def y(self, x: float) -> float:
        return self.a * self.b ** x + self.c

    def __str__(self):
        return f"y = {self.a}*{self.b}^x+{self.c}"