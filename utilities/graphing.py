from typing import List, Callable

from utilities.markers import Proxy
import numpy as np


def mpl_graph_fn(fn: Callable, start: float, end: float, dx: float = 0.1, **kwargs):
    xs = np.arange(start, end, dx)
    ys = []
    for x in xs:
        ys.append(fn(x))
    mpl_graph(xs, ys, **kwargs)


@Proxy.runInMainThread
def mpl_graph(xs: List[float], ys: List[float] = None, title: str = None, xlabel: str = 'x', ylabel: str = 'y',
              type: str = 'plot', **kwargs):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    # set center
    ax.axhline(color='black', lw=0.5)
    ax.axvline(color='black', lw=0.5)

    # plot
    fn = getattr(ax, type)
    if ys is None:
        fn(xs, **kwargs)
    else:
        fn(xs, ys, **kwargs)

    # set title
    if title is None:
        title = f"{ylabel} against {xlabel}"
    fig.suptitle(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.show()
