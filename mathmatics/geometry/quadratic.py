import math

from mathmatics.structures.vector import Vector2D


def solve_quadratic(a: int, b: int, c: int) -> Vector2D:
    equation_1 = ((-b) + math.sqrt((b ** 2) - 4 * a * c)) / (2 * a)
    equation_2 = ((-b) - math.sqrt((b ** 2) - 4 * a * c)) / (2 * a)

    return Vector2D(equation_1, equation_2)


if __name__ == '__main__':
    print(solve_quadratic(1, 3, 2))
