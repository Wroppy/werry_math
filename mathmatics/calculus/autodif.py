import math
from typing import Any

def _sign(x):
    if x > 0:
        return 1
    return -1


class DualNumber:
    real: float
    dual: float

    def __init__(self, real: Any = 0.0, dual: Any = None):
        if dual is None:
            if isinstance(real, DualNumber):
                num = real
                real = num.real
                dual = num.dual
            else:
                dual = 0.0

        self.real = real
        self.dual = dual

    def __add__(self, other: Any):
        if not isinstance(other, DualNumber):
            other = DualNumber(other)

        return DualNumber(self.real + other.real, self.dual + other.dual)

    def __sub__(self, other: Any):
        if not isinstance(other, DualNumber):
            other = DualNumber(other)

        return DualNumber(self.real - other.real, self.dual - other.dual)

    def __mul__(self, other: Any):
        if not isinstance(other, DualNumber):
            other = DualNumber(other)

        return DualNumber(self.real * other.real, self.dual * other.real + self.real * other.dual)

    def __truediv__(self, other: Any):
        if not isinstance(other, DualNumber):
            other = DualNumber(other)

        return DualNumber(self.real / other.real, (self.dual * other.real - self.real * other.dual) / other.real ** 2)

    @staticmethod
    def sin(n):
        if not isinstance(n, DualNumber):
            n = DualNumber(n)

        return DualNumber(math.sin(n.real), n.dual * math.cos(n.real))

    @staticmethod
    def cos(n):
        if not isinstance(n, DualNumber):
            n = DualNumber(n)

        return DualNumber(math.cos(n.real), -n.dual * math.sin(n.real))

    @staticmethod
    def exp(n):
        if not isinstance(n, DualNumber):
            n = DualNumber(n)

        return DualNumber(math.exp(n.real), n.dual * math.exp(n.real))

    @staticmethod
    def ln(n):
        if not isinstance(n, DualNumber):
            n = DualNumber(n)

        return DualNumber(math.log(n.real), n.dual / n.real)

    def __pow__(self, k):
        return DualNumber(math.pow(self.real, k), self.dual * k * math.pow(self.real, k - 1))

    @staticmethod
    def abs(n):
        if not isinstance(n, DualNumber):
            n = DualNumber(n)

        return DualNumber(math.fabs(n.real), n.dual * _sign(n.real))

    def __iter__(self):
        yield self.real
        yield self.dual

    @staticmethod
    def autodiff_x(fn, x):
        return fn(DualNumber(x, 1))

    @staticmethod
    def autodiff(fn):
        def diff(x):
            return fn(DualNumber(x, 1))

        return diff

    def __str__(self):
        return f"Dual({self.real} + {self.dual}e)"

    def __repr__(self):
        return f"DualNumber(real={self.real}, dual={self.dual})"


Dual = DualNumber


def xsquared(x):
    return Dual(x) ** 2


def trig_identity(x):
    return Dual.sin(x) ** 2 + Dual.cos(x) ** 2


def random_function(x):
    d = Dual(x)
    return d ** 2 + (Dual.exp(Dual.cos(d) / 2)) * Dual.sin(d * Dual.cos(d / 2)) + Dual.cos(d * 10) * Dual.abs(d - Dual.sin(d * 10))


if __name__ == '__main__':
    from mathmatics.calculus.derivative import derivative_fn
    from utilities.graphing import mpl_graph_fn2

    dfdx = Dual.autodiff(random_function)
    numerical = derivative_fn(random_function, dx=0.01)
    def fn(x):
        f, df = dfdx(x)
        dfn = numerical(x)
        return f, df, dfn.real

    mpl_graph_fn2(fn, -2, 2, 0.0001)

    # print(dfdx(4))
