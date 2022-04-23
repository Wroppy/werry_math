import random
from typing import Callable, Tuple

import numpy as np


# Using the left Riemann sums
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


def monte_carlo_integration(fn: Callable[[float], float], a: float, b: float, samples: int = 1000) -> Tuple[float, float]:
    answer = sum([fn(random.random() * (b - a) + a) for _ in range(samples)]) * (b - a) / samples
    s_var = sum([(fn(random.random() * (b - a) + a) - answer) ** 2 for _ in range(samples)]) / (samples - 1) / samples

    # include variance check
    return answer, s_var


if __name__ == '__main__':
    # compute pi
    quarter_pi, variance = monte_carlo_integration(
        lambda x: (1 - x * x) ** 0.5,
        0, 1,
        9000
    )
    pm = variance ** 0.5 * 3
    ans = quarter_pi * 4
    ans_pm = (pm / quarter_pi) * ans
    print(f"{ans - ans_pm}-{ans + ans_pm}")
