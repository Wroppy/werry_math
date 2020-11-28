import math
from typing import Callable

from mathmatics.calculus.common import sigma as __sigma
from mathmatics.calculus.derivative import derivative_fn as __derivative_fn

__two_pi = 2 * math.pi


def taylor_sin(x: float, precision: int = 7) -> float:
    """
    Returns the taylor series for sin\n
    https://www.wikiwand.com/en/Taylor_series

    :param x: X
    :param precision: Degree of polynomial
    :return: Sin of X
    """
    sign = 1
    while x > __two_pi:
        x -= __two_pi

    while x < 0:
        x += __two_pi

    if x > math.pi:
        x -= math.pi
        sign = -1

    seesaw = 1
    result = 0
    for i in range(1, precision * 2, 2):
        result += seesaw * (x ** i) / math.factorial(i)
        seesaw *= -1

    return sign * result


def taylor_cos(x: float, precision: int = 7) -> float:
    """
    Returns the taylor series for cos\n
    https://www.wikiwand.com/en/Taylor_series

    :param x: X
    :param precision: Degree of polynomial
    :return: Sin of X
    """
    sign = 1
    while x > __two_pi:
        x -= __two_pi

    while x < 0:
        x += __two_pi

    if x > math.pi:
        x -= math.pi
        sign = -1

    seesaw = 1
    result = 0
    for i in range(0, precision * 2 - 1, 2):
        result += seesaw * (x ** i) / math.factorial(i)
        seesaw *= -1

    return sign * result


def taylor_series(fn: Callable, x: float, a: float, precision: int = 7) -> float:
    """
    Returns the evaluated general taylor series for fn at x around a\n
    https://www.wikiwand.com/en/Taylor_series

    :param fn: Function to estimate
    :param x: X
    :param a: A
    :param precision: Degree of polynomial
    :return: Evaluated taylor series
    """
    return __sigma(lambda n: __derivative_fn(fn, degree=n)(a) * ((x - a) ** n / math.factorial(n)), 0, precision)


def taylor_series_fn(fn: Callable, a: float, precision: int = 7) -> Callable:
    """
    Returns the general taylor series for fn around a\n
    https://www.wikiwand.com/en/Taylor_series

    :param fn: Function to estimate
    :param a: A
    :param precision: Degree of polynomial
    :return: Taylor series for fn around a
    """
    return lambda x: taylor_series(fn, x, a, precision)


if __name__ == '__main__':
    at = 1.77 * __two_pi
    print(taylor_sin(1.77 * __two_pi))
    print(math.sin(1.77 * __two_pi))

    print(taylor_cos(1.77 * __two_pi))
    print(math.cos(1.77 * __two_pi))

    print(taylor_series(math.cos, at, at - 0.5))
    print(math.cos(at))
