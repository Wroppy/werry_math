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


if __name__ == '__main__':
    function = lambda x: x * x
    print(derivative(function, 1))
    print(derivative_fn(function)(2))
    print(derivative_fn(function, degree=0)(2))
