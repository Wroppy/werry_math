import math


def choose(n: int, k: int) -> int:
    """
    Choose function where the order does not matter

    :param n: From n
    :param k: Choose k
    :return: Amount of permutations
    """
    return int(math.factorial(n) / (math.factorial(k) * math.factorial(n - k)))


if __name__ == '__main__':
    print(choose(3, 2))