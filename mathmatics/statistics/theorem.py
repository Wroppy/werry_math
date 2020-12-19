from statistics import NormalDist
from typing import List, Union

from mathmatics.statistics.common import Dist, to_distf, rand, mean, rand_list, weighted_mean, \
    weighted_standard_deviation, standard_deviation, skew, kurtosis
from utilities.graphing import mpl_graph, calc_bins, mpl_graph_fn
import numpy as np

from utilities.markers import Proxy


@Proxy.runInMainThread
def central_limit_theorem(dist: Union[Dist, int], s: int, times: int):
    """
    Graphs the central limit theorem
    :param dist: Amount of random data
    :param s: Sample size
    :param times: Number of times to sample the data
    :return:
    """
    import matplotlib.pyplot as plt
    from matplotlib import colors
    from matplotlib.ticker import PercentFormatter

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

    bins = calc_bins(-0.5 + min(dist[0]), max(dist[0]) + 0.5, 1)

    # https://matplotlib.org/3.3.0/gallery/statistics/hist.html#updating-histogram-colors
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


def sample_dist(p_mean: float, p_std: float, s_size: int):
    s_mean = p_mean
    s_std = p_std / s_size ** 0.5
    print(f"sdsm mean: {s_mean}")
    print(f"sdsm std: {s_std}")
    mpl_graph_fn(NormalDist(s_mean, s_std).pdf, 0, 1, dx=0.001)



if __name__ == '__main__':
    sample_dist(0.56, 0.2, 100)
