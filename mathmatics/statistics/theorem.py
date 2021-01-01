from statistics import NormalDist
from typing import List, Union

from libraries.solver.nodes import *
from libraries.structures.formula import Formula
from mathmatics.statistics.common import Dist, to_distf, rand, mean, rand_list, weighted_mean, \
    weighted_standard_deviation, standard_deviation, skew, kurtosis
from utilities.graphing import mpl_graph, calc_bins, mpl_graph_fn
import numpy as np

from utilities.markers import Proxy


def central_limit_theorem(dist: Union[Dist, int], s: int, times: int):
    """
    Graphs the central limit theorem
    :param dist: Amount of random data
    :param s: Sample size
    :param times: Number of times to sample the data
    :return:
    """
    if isinstance(dist, int):
        dist = [range(dist), rand_list(dist)]

    sample_means = []

    distf = to_distf(dist)
    # samples
    for time in range(times):
        sample = []
        for _ in range(s):
            random = rand()
            cumul = 0
            for i in range(len(distf)):
                cumul += distf[i][1]
                if random <= cumul:
                    sample.append(distf[i][0])
                    break
        m = mean(sample)
        sample_means.append(m)

    print(f"population mean: {weighted_mean(dist)}")
    print(f"population std: {weighted_standard_deviation(dist)}")
    print(f"expected sdsm mean {weighted_mean(dist)}")
    print(f"expected sdsm std {weighted_standard_deviation(dist) / (s ** 0.5)}")
    print(f"sdsm mean: {mean(sample_means)}")
    print(f"sdsm std: {standard_deviation(sample_means)}")
    print(f"sdsm skew: {skew(sample_means)}")
    print(f"sdsm kurtosis: {kurtosis(sample_means)}")

    @Proxy.runInMainThread
    def graph():
        import matplotlib.pyplot as plt
        from matplotlib import colors
        from matplotlib.ticker import PercentFormatter
        # https://matplotlib.org/3.3.0/gallery/statistics/hist.html#updating-histogram-colors
        bins = calc_bins(-0.5 + min(dist[0]), max(dist[0]) + 0.5, 1)
        fig, axs = plt.subplots(1, 2, tight_layout=True)
        N, bins, patches = axs[0].hist(sample_means, bins=bins)
        fracs = N / s
        norm = colors.Normalize(fracs.min(), fracs.max())
        for thisfrac, thispatch in zip(fracs, patches):
            color = plt.cm.viridis(norm(thisfrac))
            thispatch.set_facecolor(color)

        axs[1].plot(dist[0], dist[1])
        axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))
        fig.suptitle("Sampling distribution of the sample mean")
        plt.show()

    graph()


def sample_dist(p_mean: float, p_std: float, s_size: int):
    s_mean = p_mean
    s_std = p_std / s_size ** 0.5
    print(f"sdsm mean: {s_mean}")
    print(f"sdsm std: {s_std}")
    mpl_graph_fn(NormalDist(s_mean, s_std).pdf, 0, 1, dx=0.001)


class TInterval(Formula):
    """
    The formula for the confidence interval for difference of means
    """
    description = {
        "[lower, upper]": 'The lower and upper bound for the confidence interval',
        r"\bar{x}_1": 'The sample mean of the first sample',
        r"\bar{x}_2": 'The sample mean of the second sample',
        r"t^\star": 'The critical t value',
        r"\sigma_{\bar{x}_1-\bar{x}_2}": 'The standard deviation of the sampling distribution of difference of sample means'
    }

    def to_node(self) -> Equal:
        return Symbol("[lower, upper]") == PlusMinus(
            Bracket(Symbol(r"\bar{x}_1") - Symbol(r"\bar{x}_2")),
            Symbol(r"t^{\star}") * Symbol(r"\sigma_{\bar{x}_1-\bar{x}_2}")
        )


class BayesTheoremWords(Formula):
    symbols = {"Posterior", "Prior", "Sensitivity", "FalsePositiveRate"}

    def to_node(self) -> Equal:
        po = "Posterior"
        p = "Prior"
        s = "Sensitivity"
        f = "FalsePositiveRate"
        return self.s(po) == self.s(p) * (
                self.s(s) /
                (
                        self.s(p) * self.s(s) +
                        (Number(1) - self.s(p)) * self.s(f)
                )
        )


class BayesTheoremOdds(Formula):
    description = {
        "O(H|E)": "The odds of the hypothesis given the evidence",
        "O(H)": "The odds of the hypothesis",
        "P(E|H)": "The probability of the evidence given the hypothesis",
        r"P(E|\negH)": "The probability of the evidence if the hypothesis is false"
    }

    def to_node(self) -> Equal:
        return self.s("O(H|E)") == self.s("O(H)") * (self.s("P(E|H)") / self.s(r"P(E|\negH)"))


class ChiSquared(Formula):
    description = {
        r"\chi^2": "The chi squared statistic",
        "O_i": "The observed frequency for the ith variable",
        "E_i": "The expected frequency for the ith variable",
    }

    def to_node(self) -> Equal:
        return self.s(r"\chi^2") == Sum(((self.s("O_i") - self.s("E_i")) ** Number(2)) / self.s("E_i"))


if __name__ == '__main__':
    # fo = TInterval()
    # print(fo.solvewhere({
    #     r"\bar{x}_1": 38.9,
    #     r"\bar{x}_2": 38.3,
    #     r"t^\star": 1.74,
    #     r"\sigma_{\bar{x}_1-\bar{x}_2}": 0.869
    # }))
    t = BayesTheoremOdds()
    print(t.solve())
