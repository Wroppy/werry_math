import math
import operator
from typing import Union, List, Set, Tuple

import numpy as np


class DataSet:
    """
    A container for a list of values
    """

    def __init__(self, data: Union[List[float], Set[float], Tuple[float]]):
        self.data = list(data)

    def mean(self) -> float:
        return sum(self.data) / len(self.data)

    def sort(self, *args, **kwargs) -> 'DataSet':
        self.data.sort(*args, **kwargs)
        return self

    def sorted(self, *args, **kwargs) -> list:
        data = self.data
        data.sort(*args, **kwargs)
        return data

    def median(self):
        sorted_data = self.sorted()
        data_len = int(len(sorted_data))
        if data_len % 2 == 0:
            left = sorted_data[int(data_len / 2) - 1]
            right = sorted_data[int(data_len / 2)]
            return left / 2 + right / 2
        else:
            return sorted_data[int(data_len / 2)]

    def mode(self) -> float:
        count = {}
        for num in self.data:
            if str(num) not in count:
                count[str(num)] = 0
            count[str(num)] += 1

        return int(max(count.items(), key=operator.itemgetter(1))[0])

    def to_numpy(self) -> np.array:
        return np.array(self.data)


class DataFrame:
    pass


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
