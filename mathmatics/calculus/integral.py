from typing import Callable

import numpy as np


def integral(fn: Callable, start: float, end: float, dx: float = 0.01) -> float:
    """
    Returns the definite integral for fn from start to end

    :param fn: Function to evaluate the integral of
    :param start: Start of the definite integral
    :param end: End of the definite integral
    :param dx: dx
    :return: Evaluated result
    """
    result = 0
    for x in np.arange(start, end, dx):
        result += fn(x) * dx
    return result
