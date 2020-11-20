from typing import Tuple, List

from mathmatics.exceptions.common import EquationNotEnoughArguments
from mathmatics.geometry.equation import ExponentialEquation


def table_to_exponent(table: List[Tuple[float, float]], asymptote: float = 0) -> ExponentialEquation:
    if len(table) < 2:
        raise EquationNotEnoughArguments

    y1 = table[0][1]
    y2 = table[1][1]
    x1 = table[0][0]
    x2 = table[1][0]

    b = (y2 / y1) ** (1 / (x2 - x1))
    a = (y1 - asymptote) / b ** x1
    return ExponentialEquation(a, b, asymptote)


if __name__ == '__main__':
    eq = ExponentialEquation(125, 1.2)
    eq.print_y(2)
