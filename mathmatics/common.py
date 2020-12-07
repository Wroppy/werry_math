from typing import List

from utils.markers import Proxy


@Proxy.runInMainThread
def mpl_graph(xs: List[float], ys: List[float], title: str = None, xlabel: str = 'x', ylabel: str = 'y',
              type: str = 'plot'):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    # set center
    ax.axhline(color='black', lw=0.5)
    ax.axvline(color='black', lw=0.5)

    # plot
    fn = getattr(ax, type)
    fn(xs, ys)

    # set title
    if title is None:
        title = f"{ylabel} against {xlabel}"
    fig.suptitle(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.show()


def translate(value: float, left_min: float, left_max: float, right_min: float = 0, right_max: float = 1):
    """
    https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    """
    left_span = left_max - left_min
    right_span = right_max - right_min

    value_scaled = float(value - left_min) / float(left_span)

    return right_min + value_scaled * right_span
