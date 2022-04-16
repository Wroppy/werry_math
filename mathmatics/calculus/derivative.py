from typing import Callable

from mathmatics.exceptions.common import DerivativeNegativeDegree


def derivative(fn: Callable, x: float, dx: float = 0.01) -> float:
    """
    Returns the evaluated limit definition of derivative\n
    https://www.wikiwand.com/en/Derivative

    :param fn: Function to evaluate the derivative of
    :param x: X
    :param dx: H
    :return: The evaluation of the derivative at X
    """
    return (fn(x + dx) - fn(x)) / dx


def derivative_fn(fn: Callable, degree: int = 1, dx: float = 0.01) -> Callable:
    """
    Returns the limit definition of derivative as a function

    :param fn: Function to take the derivative of
    :param degree: Degree of derivative
    :param dx: H
    :return: The derivative function of fn
    """
    if degree < 0:
        raise DerivativeNegativeDegree

    if degree == 0:
        return fn

    # function creator because scoping issues
    # https://stackoverflow.com/questions/233673/how-do-lexical-closures-work
    def fnC(fn: Callable):
        def func(x): return derivative(fn, x, dx)

        return func

    der = fnC(fn)
    for _ in range(1, degree):
        tmp = der
        der = fnC(tmp)
    return der


def inverse_function(func: Callable, a: float, b: float, c: float = None, dx=0.01):
    """
    Return the inverse function of *func*, with region from a to b,
    using a Taylor expansion of degree 3 at alpha=c, with derivative accuracy dx.

    :param func: The function to be inversed
    :param a: Starting region block
    :param b: Ending region block
    :param c: Taylor alpha
    :param dx: Derivative step
    :return: The inverse function of *func*
    """
    # TODO: Make this go up degrees

    if c is None:
        c = (a + b) / 2

    def inverse(y):
        fc = func(c)
        df = derivative_fn(func, 1, dx)(c)
        ddf = derivative_fn(func, 2, dx)(c)
        dddf = derivative_fn(func, 3, dx)(c)
        return c + 1 / df * (y - fc) - ddf / (2 * df ** 3) * (y - fc) ** 2 + (3 * ddf ** 2 - dddf * df) / (
                    6 * df ** 5) * (y - fc) ** 3

    return inverse

if __name__ == '__main__':
    from utilities.graphing import mpl_graph_fn
    # function = lambda x: x * x
    # print(derivative(function, 1))
    # print(derivative_fn(function)(2))
    # print(derivative_fn(function, degree=0)(2))

    def test(x):
        return 2.7182818 ** x

    # print(inverse_function(test, -1, 10)(1.25))
    mpl_graph_fn(inverse_function(test, -4, 3), 0.1, 2)