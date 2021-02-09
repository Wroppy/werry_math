from typing import Tuple


def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield frozenset({ss for mask, ss in zip(masks, s) if i & mask})


def divide(b: float, a: float) -> Tuple[float, float]:
    """
    Returns the quotient and positive remainder as a tuple when *left* / *right*
    b = aq + r

    :param b: b
    :param a: a
    :return: quotient, remainder
    """
    sign = 1
    if b < 0 and a > 0:
        sign = -1

    q = 0
    while True:
        r = b - (q * a)
        if 0 <= r < abs(a):
            break
        q += sign

    return q, b - (q * a)


def print_divide(left: float, right: float):
    quotient, remainder = divide(left, right)
    return f"{left}/{right} => {quotient}...{remainder}"


def gcd(b: float, a: float) -> float:
    while a:
        b, a = a, b % a

    return abs(b)


def gcd_step(b: float, a: float) -> float:
    while a:
        print(f"{b} = {a}({int((b - b % a) / a)}) + {b % a}")
        b, a = a, b % a

    return abs(b)


def all_sets(alpha: int = 2):
    v_a = set()
    for a in range(alpha):
        v_a = frozenset(powerset(v_a))

    return v_a


if __name__ == '__main__':
    print(str(all_sets()).replace('frozenset()', 'o').replace('frozenset', '').replace('(', '').replace(')', ''))
