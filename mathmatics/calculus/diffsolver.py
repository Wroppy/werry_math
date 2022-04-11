from abc import ABC, abstractmethod
from typing import Callable

import numpy as np


class DiffEqSolverBase(ABC):
    @abstractmethod
    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        pass

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
        while t <= tf:
            out.append((t, y))

            y = y + self.step_size * equation(t, y)
            t = t + self.step_size

        return out


class MidpointMethod(DiffEqSolverBase):
    def __init__(self, step_size: float = 0.1):
        super()

        self.step_size = step_size

    def _solve(self, equation: Callable, e0, t0: float, tf: float):
        out = []

        y = e0
        t = t0
        while t <= tf:
            out.append((t, y))

            # estimate the y' at midpoint
            h = self.step_size
            tm = t + h / 2
            dydtm = y + h / 2 * equation(t, y)

            y = y + h * equation(tm, dydtm)
            t = t + h

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
        while t <= tf:
            out.append((t, y))

            k1 = f(t, y)
            k2 = f(t + h / 2, y + h / 2 * k1)
            k3 = f(t + h / 2, y + h / 2 * k2)
            k4 = f(t + h, y + h * k3)

            y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            t = t + h

        return out


def test_dif(t, q):
    y, v = q
    return -40 * y


if __name__ == '__main__':
    from utilities.graphing import mpl_graph

    solver = RK4Method(step_size=0.2)
    # solver = MidpointMethod(step_size=0.2)
    ans = solver.solve(test_dif, [2, 0], 0, 5)
    xs = [p[0] for p in ans]
    ys = [p[1] for p in ans]

    mpl_graph(xs, ys)
