import math
import operator
import random
from statistics import NormalDist
from typing import Union, List, Set, Tuple, Optional

import numpy as np
import scipy
from scipy import stats

from mathmatics.calculus.common import sigma
from mathmatics.structures.line import Ray2D
from mathmatics.structures.vector import Vector2D

Dist = List[List[float]]
DistF = List[List[float]]

Data = List[float]
Table = List[List[float]]


def to_dist(distf: DistF) -> Dist:
    xs = []
    ys = []
    for x, y in distf:
        xs.append(x)
        ys.append(y)
    return [xs, ys]


def to_distf(dist: Dist) -> DistF:
    distf = []
    for i in range(len(dist[0])):
        distf.append([dist[0][i], dist[1][i]])
    return distf


def rand(mi: float = 0, ma: float = 1) -> float:
    return mi + (ma - mi) * random.random()


def rand_list(n: int = 10) -> List[float]:
    final = []
    for i in range(n):
        final.append(rand())

    total = sum(final)
    for i in range(len(final)):
        final[i] /= total

    return final


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


def skew(data: List[float]) -> float:
    _len = len(data)
    _mean = mean(data)
    _std = standard_deviation(data)
    _sum = sigma(lambda i: ((data[i] - _mean) / _std) ** 3, 0, _len - 1)
    return _sum / _len


def kurtosis(data: List[float]) -> float:
    _len = len(data)
    _mean = mean(data)
    _std = standard_deviation(data)
    _sum = sigma(lambda i: ((data[i] - _mean) / _std) ** 4, 0, _len - 1)
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


def weighted_mean(data: Dist) -> float:
    final = 0
    distf = to_distf(data)
    for weight, prob in distf:
        final += weight * prob
    return final


def weighted_variance(data: Dist) -> float:
    _mean = weighted_mean(data)
    return sigma(lambda n: data[1][n] * (data[0][n] - _mean) ** 2, 0, len(data[0]) - 1)


def weighted_standard_deviation(data: Dist) -> float:
    _variance = weighted_variance(data)
    return math.sqrt(_variance)


def ztable(z_score: float) -> float:
    return NormalDist().cdf(z_score)


def ztable_advance(mean: float, std: float, value: float) -> float:
    return NormalDist(mean, std).cdf((value - mean) / std)


def ztable_reverse(percent: float) -> float:
    return NormalDist().inv_cdf(percent)


def zstar(percent: float) -> float:
    return abs(ztable_reverse((1 - percent) / 2))


def confidence_interval(s_mean: float, n: int, percent: float = 0.95) -> Tuple[float, float]:
    bottom = ztable_reverse((1 - percent) / 2)
    top = -bottom

    s_std = (s_mean * (1 - s_mean) / n) ** 0.5
    top_value = s_mean + top * s_std
    bottom_value = s_mean + bottom * s_std

    return bottom_value, top_value


def confidence_interval_std(s_mean: float, n: int, s_std: float, percent: float = 0.95) -> Tuple[float, float]:
    bottom = ztable_reverse((1 - percent) / 2)
    top = -bottom

    top_value = s_mean + top * s_std / n ** 0.5
    bottom_value = s_mean + bottom * s_std / n ** 0.5

    return bottom_value, top_value


def ttable(t_score: float, n: int):
    return stats.t.cdf(t_score, n)


def ttable_reverse(percent: float, n: int):
    return stats.t.ppf(percent, n)


def tstar(percentage: float, n: int):
    return abs(ttable_reverse((1 - percentage) / 2, n))


def confidence_interval_mean(s_mean: float, n: int, s_std: float, percent: float = 0.95) -> Tuple[float, float]:
    t_star = tstar(percent, n - 1)

    interval = t_star * s_std / n ** 0.5

    return s_mean - interval, s_mean + interval


def chi_square_test(expected: Data, observed: Data) -> float:
    return sigma(lambda i: (expected[i] - observed[i]) ** 2 / expected[i], 0, len(expected) - 1)


def chi_square_table(value: float, df: int) -> float:
    return scipy.stats.chi2.cdf(value, df)


# [[11,  3,  8],
#  [ 2,  9, 14],
#  [12, 13, 28]]
def chi_square_table_test(table: Table) -> Tuple[float, float]:
    # get totals
    row_totals = []
    col_totals = []

    for row in table:
        row_totals.append(sum(row))

    for col in range(len(table[0])):
        col_totals.append(sum([row[col] for row in table]))

    table_total = sum(row_totals)

    # calculate expected
    expected = []
    for row in row_totals:
        r = []
        for col in col_totals:
            r.append(row * col / table_total)
        expected.append(r)

    chi_square = 0
    for ri, row in enumerate(table):
        for ci, col in enumerate(row):
            chi_square += (col - expected[ri][ci]) ** 2 / expected[ri][ci]

    p_value = 1 - chi_square_table(chi_square, (len(row_totals) - 1) * (len(col_totals) - 1))
    return chi_square, p_value


if __name__ == '__main__':
    print(chi_square_table_test([[11, 3, 8], [2, 9, 14], [12, 13, 28]]))
