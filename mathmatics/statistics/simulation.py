from statistics import NormalDist

from utilities.graphing import mpl_graph_fn
from utilities.markers import Proxy


@Proxy.runInMainThread
def distribution_of_sample_proportions(p_success: float, s: int):
    # 0.90, 1000

    # normal dist here
    dist = NormalDist(p_success, p_success * (1 - p_success) / s ** 0.5)
    mpl_graph_fn(dist.pdf, 0, 1.0, dx=0.01)


if __name__ == '__main__':
    distribution_of_sample_proportions(0.9, 1000)
    distribution_of_sample_proportions(0.92, 1000)