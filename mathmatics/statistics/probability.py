import math
from typing import List

from mathmatics import sigma


def bayes_theorem(pH: float, pEH: float, pnEH: float = None) -> float:
    """
    Calculates the bayes theorem for probability that a hypothesis given an evidence

    :param pH: p(Hypothesis)
    :param pEH: p(Evidence given Hypothesis)
    :param pnEH: p(Evidence given ~Hypothesis)
    :return: p(Hypothesis given Evidence)
    """
    if pnEH is None:
        pnEH = 1 - pEH
    return pH * pEH / (pH * pEH + (1 - pH) * pnEH)


def p_and(pA: float, pB: float) -> float:
    return pA * pB


def p_or(pA: float, pB: float, pAandB: float = 0.0) -> float:
    return pA + pB - pAandB


# [ [x1 x2 x3]
#   [p1 p2 p3] ]
def p_mean(data: List[List[float]]) -> float:
    result = 0
    xs = data[0]
    ps = data[1]
    for i in range(len(xs)):
        result += xs[i] * ps[i]

    return result


def p_variance(data: List[List[float]]) -> float:
    _mean = p_mean(data)
    xs = data[0]
    ps = data[1]
    return sigma(
        lambda i: ((xs[i] - _mean) ** 2) * ps[i],
        0,
        len(xs) - 1
    )

def p_standard_deviation(data: List[List[float]]) -> float:
    return math.sqrt(p_variance(data))


if __name__ == '__main__':
    print(bayes_theorem(1 / 21, 0.4, 0.1))
