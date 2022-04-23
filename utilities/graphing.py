import math
from typing import List, Callable, Union

from utilities.markers import Proxy
import numpy as np
import csv


def mpl() -> str:
    return 'import matplotlib.pyplot as plt'


def calc_bins(mi: float, ma: float, width: float):
    return np.arange(mi, ma + width, width)


def mpl_graph_fn2(fn: Callable, start: float, end: float, dx: float = 0.1, **kwargs):
    xs = np.arange(start, end, dx)
    yss = []
    for x in xs:
        yss.append(fn(x))

    if len(yss) == 0:
        raise Exception("no points to graph")

    ys = [
        [yss[i][j] for i in range(len(yss))]
        for j in range(len(yss[0]))
    ]

    mpl_graph(list(xs), ys, **kwargs)


def mpl_graph_fn(fn: Callable, start: float, end: float, dx: float = 0.1, **kwargs):
    xs = np.arange(start, end, dx)
    ys = []
    for x in xs:
        ys.append(fn(x))
    mpl_graph(list(xs), ys, **kwargs)


@Proxy.runInMainThread
def mpl_vector_field2(fn: Callable, x_start: float, x_end: float, x_gap: float, y_start: float, y_end: float,
                      y_gap: float, *args, **kwargs):
    import matplotlib.pyplot as plt

    X, Y = np.meshgrid(np.linspace(x_start, x_end, math.ceil((x_end - x_start) / x_gap)),
                       np.linspace(y_start, y_end, math.ceil((y_end - y_start) / y_gap)))

    u, v = fn(X, Y)

    fig, ax = plt.subplots()
    ax.quiver(X, Y, u, v, angles='xy', scale_units='xy', scale=1, *args, **kwargs)
    plt.show()



@Proxy.runInMainThread
def mpl_graph(xs: List[float], ys: Union[List[float], List[List[float]]] = None, title: str = None, xlabel: str = 'x',
              ylabel: str = 'y',
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
    elif isinstance(ys, (list, np.ndarray)) and len(ys) > 0 and isinstance(ys[0], (list, np.ndarray)):
        for i, y in enumerate(ys):
            fn(xs, y, **kwargs, label=f"{ylabel}{i}")
    else:
        fn(xs, ys, **kwargs, label=ylabel)

    # set title
    if title is None:
        title = f"{ylabel} against {xlabel}"
    fig.suptitle(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # add legend
    plt.legend()

    plt.show()
