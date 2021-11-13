import numpy as np

from mathmatics.calculus.ft import fourier_transform
from utilities.markers import Proxy


def _slit_function(b):
    def f(t):
        if abs(t) <= b / 2:
            return 1
        return 0

    return f


@Proxy.runInMainThread
def single_slit(view_width: float, gap_width: float, dx: float = 0.01):
    """
    Displays the single slit diffraction pattern using Fourier transform.

    Explanation Notes:
    https://web.pa.msu.edu/courses/2010fall/PHY431/PostNotes/PHY431-Slides-Diffraction.pdf

    :param view_width: The width of the position view.
    :param gap_width: The width of the slit
    :param dx: Accuracy of the Fourier transform.
    """
    import matplotlib.pyplot as plt

    half_vw = view_width / 2

    # plot two plots
    fig, axs = plt.subplots(2)

    # plot slit
    slit = _slit_function(gap_width)
    xs = np.arange(-half_vw, half_vw, dx)
    ys = np.array([slit(x) for x in xs])
    axs[0].plot(xs, ys)
    # set subplot title, x and y labels
    axs[0].set_title("Single Slit Aperture (Transmission) Function")
    axs[0].set_xlabel("Position")
    axs[0].set_ylabel("Transmission")


    xs = np.arange(-half_vw, half_vw, dx)
    ys = np.array([fourier_transform(slit, x).real ** 2 for x in xs])
    axs[1].plot(xs, ys)
    axs[1].set_title("Single Slit Interference Intensity Function")
    axs[1].set_ylabel("Intensity")
    axs[1].set_xlabel("Projected Electric Field Location domain")

    plt.show()
