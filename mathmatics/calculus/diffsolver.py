import math
from abc import ABC, abstractmethod
from typing import Callable, Tuple

import numpy as np

from mathmatics.structures.matrix import Matrix


class DiffEqSolverBase(ABC):
    @abstractmethod
    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        pass

    def integrate(self, equation: Callable, a: float, b: float):
        """
        Integrate a y-independent equation from t=a to t=b

        :param equation: The integrand
        :param a: t=a
        :param b: t=b
        :return:
        """

        sign = 1
        if a > b:
            sign = -1
            a, b = b, a

        def dydt(t, q):
            return equation(t)

        e = equation(a)
        out = self._solve(dydt, e, a, b)
        return (out[-1][1] - out[0][1]) * sign

    def solve(self, equation: Callable, e0, t0: float, tf: float):
        """
        Solve a differential equation *equation* with initial conditions *e0*, from t0 to tf

        :param equation: The differential equation of form (t, q) -> num
        :param e0: The initial conditions, could be a list
        :param t0: THe initial time
        :param tf: The final time
        :return: A list of (time, q) pairs
        """
        if isinstance(e0, list):
            initial = np.asarray(e0)
        else:
            initial = e0

        def dzdt(t, q):
            if isinstance(q, np.ndarray):
                return np.asarray([*q[1:], equation(t, q)])
            return equation(t, q)

        return self._solve(dzdt, initial, t0, tf)


class EulersMethod(DiffEqSolverBase):
    def __init__(self, step_size: float = 0.1):
        super()

        self.step_size = step_size

    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        out = []

        y = e0
        t = t0
        out.append((t, y))
        while t <= tf:
            y = y + self.step_size * equation(t, y)
            t = t + self.step_size
            out.append((t, y))

        return out


class MidpointMethod(DiffEqSolverBase):
    def __init__(self, step_size: float = 0.1):
        super()

        self.step_size = step_size

    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        out = []

        y = e0
        t = t0
        out.append((t, y))

        while t <= tf:
            # estimate the y' at midpoint
            h = self.step_size
            tm = t + h / 2
            dydtm = y + h / 2 * equation(t, y)

            y = y + h * equation(tm, dydtm)
            t = t + h

            out.append((t, y))

        return out


class RK4Method(DiffEqSolverBase):
    def __init__(self, step_size: float = 0.1):
        super()

        self.step_size = step_size

    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        out = []

        f = equation
        h = self.step_size

        y = e0
        t = t0
        out.append((t, y))

        while t <= tf:
            k1 = f(t, y)
            k2 = f(t + h / 2, y + h / 2 * k1)
            k3 = f(t + h / 2, y + h / 2 * k2)
            k4 = f(t + h, y + h * k3)

            y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            t = t + h

            out.append((t, y))

        return out


def summation(lst):
    total = 0
    for l in lst:
        if isinstance(total, int) and total == 0:
            total = l
        else:
            total += l
    return total


class RKMethod(DiffEqSolverBase):
    METHODS = {
        'rk4': (Matrix([
            [0.5, 0, 0],
            [0, 0.5, 0],
            [0, 0, 1],
        ]), [0, 0.5, 0.5, 1], [1 / 6, 1 / 3, 1 / 3, 1 / 6]),
        '3/8': (
            Matrix([
                [1 / 3, 0, 0],
                [-1 / 3, 1, 0],
                [1, -1, 1]
            ]),
            [0, 1 / 3, 2 / 3, 1],
            [1 / 8, 3 / 8, 3 / 8, 1 / 8]
        ),
        'euler': (
            Matrix([]),
            [0],
            [1]
        ),
        'midpoint': (
            Matrix([
                [1 / 2]
            ]),
            [0, 1 / 2],
            [0, 1]
        )
    }

    def __init__(self, step_size: float = 0.1, tableu: Tuple[Matrix, Tuple[float], Tuple[float]] = None,
                 method: str = 'rk4'):
        super()

        if tableu is None:
            # this might throw exception
            tableu = RKMethod.METHODS[method]

        self.step_size = step_size
        self.tableu = tableu

    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        out = []

        f = equation
        h = self.step_size
        table, cs, bs = self.tableu

        y = e0
        t = t0
        out.append((t, y))

        while t <= tf:
            order = len(cs)
            ks = [0] * order
            for i in range(0, order):
                # table[i-1] because implicit zero first row
                ks[i] = f(t + h * cs[i], y + h * summation([table[i - 1][j] * ks[j] for j in range(0, i)]))

            y = y + h * summation([bs[i] * ks[i] for i in range(0, order)])
            t = t + h

            out.append((t, y))

        return out


# TODO: make RKMethod with error acceptance and implicit methods

def _test_dif(t, q):
    import math
    y = q
    # return -40 * y
    return t * t


if __name__ == '__main__':
    from utilities.graphing import mpl_graph
    from mathmatics.calculus.integral import integral

    fn = lambda x: math.sqrt(max(1 - x**2, 0))
    solver = RKMethod(step_size=0.000001, method='rk4')
    # print(solver.integrate(fn, 0, 10))
    print(4 * solver.integrate(fn, 0, 1))
    # solver = EulersMethod(step_size=0.001)
    # ans = solver.solve(test_dif, 0, 0, 2)
    # xs = [p[0] for p in ans]
    # ys = [p[1] for p in ans]
    #
    # if isinstance(ys[0], (list, np.ndarray)):
    #     yss = [[y[i] for y in ys] for i in range(len(ys[0]))]
    #     mpl_graph(xs, yss)
    # else:
    #     mpl_graph(xs, ys)
