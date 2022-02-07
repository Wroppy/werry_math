import math
from decimal import Decimal


def calculate_pi(accuracy: int = 10):
    total = Decimal(0)
    for k in range(0, accuracy):
        top = Decimal(1)
        for t in range(0, k):
            top *= Decimal(0.5) - t

        if k % 2 == 0:
            total += top / math.factorial(k) / (2 * k + 1)
        else:
            total -= top / math.factorial(k) / (2 * k + 1)

    return total * 4


if __name__ == '__main__':
    print(calculate_pi(4))
