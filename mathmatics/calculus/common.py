from typing import Callable


def sigma(fn: Callable, n: int, to: int) -> float:
    """
    The sigma function, a weaker form of an integral

    :param fn: Function to sum of
    :param n: Bottom bound
    :param to: Upper bound
    :return: Sigma result
    """
    result = 0
    for x in range(n, to):
        result += fn(x)
    return result
