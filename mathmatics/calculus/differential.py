from typing import Callable, Tuple


def eulers_method(dydx: Callable, initial: Tuple[float, float], dx: float = 1):
    xi, yi = initial

    def eval(x: float):
        assert x >= xi, "x is larger than initial x"

        cx = xi
        cy = yi
        while cx < x:
            dy = dydx(cx, cy)
            cx, cy = cx + dx, cy + dy * dx

        return cy

    return eval


if __name__ == '__main__':
    print(eulers_method(lambda x, y: x - 2*y+2, (0, 2), 1.2)(2.4))
