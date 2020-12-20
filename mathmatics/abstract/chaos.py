from typing import List

import numpy as np
import matplotlib.pyplot as plt

from mathmatics.common import translate
from utilities.graphing import mpl_graph
from utilities.markers import Proxy


class LogisticMap:
    def __init__(self, r: float, p0: float, rand: bool = False):
        self.r = r
        self.p0 = p0

        if rand:
            self.n = p0
            for _ in range(5):
                self.next_float()
        self.n = p0

    def n_plus_one(self, n: float) -> float:
        return self.r * n * (1 - n)

    def asymptote(self, n_to: int = 1000, leeway: float = 0.05) -> List[float]:
        memory = []

        ys = [self.p0]
        for i in range(n_to):
            yn = self.n_plus_one(ys[i])
            ys.append(yn)

            exist = False
            for m in memory:
                if abs(m[0] - yn) < leeway:
                    m[1] += 1
                    exist = True
                    break
            if not exist:
                memory.append([yn, 1])

        percentage = 1 / len(memory)
        results = []
        for i in range(len(memory) - 1, -1, -1):
            mi = memory[i]
            if mi[1] / n_to < percentage:
                pass
            else:
                results.append(mi[0])
        results.sort()
        return results

    def graph_p(self, n_to: int = 50):
        xs = list(range(0, n_to))
        ys = [self.p0]
        for i in range(len(xs) - 1):
            ys.append(self.n_plus_one(ys[i]))

        mpl_graph(xs, ys, xlabel="Days elapsed", ylabel="Population", type='scatter')

    def next_float(self) -> float:
        self.n = self.n_plus_one(self.n)
        while self.n > 0.8 or self.n < 0.2:
            self.n = self.n_plus_one(self.n)
        # map from 0.1-0.9 to 0-1

        return translate(self.n, 0.2, 0.8, 0, 1)

    @staticmethod
    @Proxy.runInMainThread
    def graph_r(rl: float = 1.1, ru: float = 4, dr: float = 0.05, p0: float = 0.5):
        plt.xlabel('r')
        plt.ylabel('asy')

        max_branch = len(LogisticMap(ru, p0).asymptote())

        for b in range(0, max_branch):
            rs = list(np.arange(rl, ru, dr))
            ys = []
            for i in range(len(rs) - 1, -1, -1):
                r = rs[i]
                asy = LogisticMap(r, p0).asymptote()
                if b > len(asy) - 1:
                    rs.pop(i)
                    continue
                ys.append(asy[b])

            ys.reverse()
            plt.scatter(rs, ys)

        plt.show()


if __name__ == '__main__':
    map = LogisticMap(3.789, 0.7, rand=True)
    rands = []
    for i in range(40000):
        n = map.next_float()
        print(n)
        rands.append(n)
    plt.hist(rands)
    plt.show()