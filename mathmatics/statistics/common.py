import math
import operator
from typing import Union, List, Set, Tuple, Optional

import numpy as np

from mathmatics.calculus.common import sigma
from mathmatics.structures.line import Ray2D
from mathmatics.structures.vector import Vector2D


class DataSet:
    """
    A container for a list of values
    """

    def __init__(self, data: Union[List[float], Set[float], Tuple[float]]):
        self.data = list(data)

    def sort(self, *args, **kwargs) -> 'DataSet':
        self.data.sort(*args, **kwargs)
        return self

    def sorted(self, *args, **kwargs) -> list:
        data = self.data
        data.sort(*args, **kwargs)
        return data

    def mean(self) -> float:
        return mean(self.data)

    def median(self):
        return median(self.data)

    def mode(self) -> float:
        return mode(self.data)

    def m_range(self) -> float:
        return m_range(self.data)

    def to_numpy(self) -> np.array:
        return np.array(self.data)


class DataFrame:
    pass


def to_list(data: str, separator=' ') -> List[float]:
    result = []
    for n in data.split(separator):
        result.append(float(n))
    return result


# permutation
def permutation(n: int, k: int) -> int:
    return int(math.factorial(n) / math.factorial(n - k))


# combination
def choose(n: int, k: int) -> int:
    """
    Choose function where the order does not matter

    :param n: From n
    :param k: Choose k
    :return: Amount of permutations
    """
    return int(math.factorial(n) / (math.factorial(k) * math.factorial(n - k)))


def mean(data: List[float]) -> float:
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    data.sort()
    data_len = int(len(data))
    if data_len % 2 == 0:
        left = data[int(data_len / 2) - 1]
        right = data[int(data_len / 2)]
        return left / 2 + right / 2
    else:
        return data[int(data_len / 2)]


def mode(data: List[float]) -> float:
    count = {}
    for num in data:
        if str(num) not in count:
            count[str(num)] = 0
        count[str(num)] += 1

    return int(max(count.items(), key=operator.itemgetter(1))[0])


def m_range(data: List[float]) -> float:
    return abs(max(data) - min(data))


def lower_quartile(data: List[float]) -> float:
    data.sort()
    _len = len(data)
    return median(data[:int(_len / 2)])


def upper_quartile(data: List[float]) -> float:
    data.sort()
    _len = len(data)
    if _len % 2 == 0:
        return median(data[int(_len / 2):])
    else:
        return median(data[int(_len / 2) + 1:])


def inter_quartile_range(data: List[float]) -> float:
    return abs(lower_quartile(data) - upper_quartile(data))


def variance(data: List[float]) -> float:
    _len = len(data)
    _mean = mean(data)
    _sum = sigma(lambda i: (data[i] - _mean) ** 2, 0, _len - 1)
    return _sum / _len


def sample_variance(data: List[float]) -> float:
    _len = len(data)
    _mean = mean(data)
    _sum = sigma(lambda i: (data[i] - _mean) ** 2, 0, _len - 1)
    return _sum / (_len - 1)


def standard_deviation(data: List[float]) -> float:
    return math.sqrt(variance(data))


def sample_standard_deviation(data: List[float]) -> float:
    return math.sqrt(sample_variance(data))


def outliers(data: List[float], multiplier: float = 1.5) -> List[float]:
    _inter_quartile_range = inter_quartile_range(data)
    _lower_quartile = lower_quartile(data)
    _upper_quartile = upper_quartile(data)
    _lower = _lower_quartile - multiplier * _inter_quartile_range
    _upper = _upper_quartile + multiplier * _inter_quartile_range
    result = []
    for d in data:
        if d < _lower or d > _upper:
            result.append(d)
    return result


def percentile(data: List[float], value: Optional[float] = None) -> Union[Optional[float], List[float]]:
    if value is None:
        result = []
        for d in data:
            result.append(percentile(data, d))
        return result

    data.sort()
    result = 0
    for d in data:
        if d >= value:
            return result / len(data)
        else:
            result += 1
    return None


def z_score(data: List[float], value: Optional[float] = None) -> Union[Optional[float], List[float]]:
    if value is None:
        result = []
        for d in data:
            result.append(z_score(data, d))
        return result
    _mean = mean(data)
    _standard_deviation = standard_deviation(data)
    return (value - _mean) / _standard_deviation


def sample_z_score(data: List[float], value: Optional[float] = None) -> Union[Optional[float], List[float]]:
    if value is None:
        result = []
        for d in data:
            result.append(z_score(data, d))
        return result
    _mean = mean(data)
    _standard_deviation = sample_standard_deviation(data)
    return (value - _mean) / _standard_deviation


# [ [x1 x2 x3]
#   [y1 y2 y3] ]
def regression(data: List[List[float]]) -> float:
    n = len(data[0])
    xs = data[0]
    ys = data[1]
    xmean = mean(xs)
    ymean = mean(ys)
    xstd = sample_standard_deviation(xs)
    ystd = sample_standard_deviation(ys)
    return (1 / (n - 1)) * sigma(lambda i: ((xs[i] - xmean) / xstd) * ((ys[i] - ymean) / ystd), 0, n - 1)


def regression_line(data: List[List[float]]) -> Ray2D:
    xs = data[0]
    ys = data[1]
    m = regression(data) * (sample_standard_deviation(ys) / sample_standard_deviation(xs))
    sample = Vector2D(mean(xs), mean(ys))
    return Ray2D.from_gradient_and_sample(m, sample)


def residuals(data: List[List[float]], r_line: Ray2D = None):
    if r_line is None:
        r_line = regression_line(data)
    xs = data[0]
    ys = data[1]
    n = len(xs)
    result = []
    for i in range(n):
        result.append(ys[i] - r_line.y(xs[i]))
    return result


def root_mean_square_error(data: List[List[float]], r_line: Ray2D = None):
    if r_line is None:
        r_line = regression_line(data)
    xs = data[0]
    ys = data[1]
    n = len(xs)
    return math.sqrt(sigma(lambda i: (ys[i] - r_line.y(xs[i])) ** 2, 0, n - 1) / (n - 2))


if __name__ == '__main__':
    print(choose(3, 2))
