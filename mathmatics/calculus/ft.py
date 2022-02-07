import cmath
import math

import numpy as np

from utilities.markers import Proxy
from functools import lru_cache


def inverse_fourier_transform(F, t):
    """
    The Inverse Fourier Transform from F(v) to f(t)

    Using the input function F(v),
    which returns the amplitude+i*phase-shift of the sinusoidal makeups of the original f(t)

    Returns a function of the time domain evaluated at time t

    :param F: complex function of the frequency domain
    :param t: time
    :return: complex function of the time domain at time *t*
    """

    infty = 100

    total = 0
    x = -infty
    while x <= infty:
        total += F(x) * cmath.exp(2j * cmath.pi * x * t) * 0.01
        x += 0.01

    return total


def fourier_transform(f, v):
    """
    The Fourier Transform from f(t) to F(v)

    Using the input function f(t),
    which returns intensity of the original f(t) at time t

    Returns a function of the frequency domain evaluated at frequency v

    :param f: complex function of the time domain
    :param v: frequency
    :return: complex function of the frequency domain at frequency *v*
    """

    infty = 100

    total = 0
    x = -infty
    while x <= infty:
        total += f(x) * cmath.exp(-2j * cmath.pi * v * x) * 0.01
        x += 0.01

    return total


def discrete_fourier_transform(points, v):
    """
    The Discrete Fourier Transform from f(t) to F(v), evaluated at the frequency v

    :param points: The samples
    :param v: The input frequency relative to the sample period
    :return: The complex fourier coefficient at the frequency v
    """
    N = len(points)
    term = sum([points[n] * cmath.exp(-2j * cmath.pi / N * v * n) for n in range(N)])
    return term


def discrete_fourier_transform_normalized(points, v, T):
    """
    The Normalized Discrete Fourier Transform from f(t) to F(v), evaluated at the frequency v

    :param points: The samples
    :param v: The absolute input frequency
    :param T: The sample period
    :return: The complex fourier coefficient at the frequency v
    """

    return discrete_fourier_transform(points, v * T) / len(points)


def inverse_discrete_fourier_transform(coefficients, t):
    """
    The Inverse Discrete Fourier Transform from F(v) to f(t), evaluated at time t

    :param coefficients: The fourier complex coefficients
    :param t: The time to be evaluated at
    :return:
    """

    N = len(coefficients)
    term = sum([coefficients[k] * cmath.exp(2j * cmath.pi / N * k * t) for k in range(N)])
    return term


def inverse_discrete_fourier_transform_normalized(coefficients, t, T):
    """
    The Normalized Inverse Discrete Fourier Transform from F(v) to f(t), evaluated at time t

    :param coefficients: The fourier complex coefficients
    :param t: The time to be evaluated at
    :param T: The sample period
    :return:
    """

    # TODO: Fix this
    return inverse_discrete_fourier_transform(list(map(lambda c: c * len(coefficients), coefficients)), t / T)


@Proxy.runInMainThread
def simulate_discrete_fourier_transform(fn=lambda x: math.sin(2 * math.pi * x), samples=8, T=1.0):
    from matplotlib import pyplot as plt

    fig, axs = plt.subplots(3, constrained_layout=True)

    xs = np.arange(0, T, 1 / samples)
    ys = [fn(x) for x in xs]
    axs[0].plot(xs, ys, 'o')
    axs[0].set_title('Original Signal')

    _xs = range(int(samples / 2))
    _ys = [discrete_fourier_transform(ys, v) * 2 / samples for v in _xs]

    _ms = [cmath.polar(y)[0] for y in _ys]
    axs[1].plot(_xs, _ms, 'o')
    axs[1].set_title('Fourier Coefficients real values')

    _ps = [cmath.polar(y)[1] for y in _ys]
    axs[2].plot(_xs, _ps, 'o')
    axs[2].set_title('Fourier Coefficients imaginary values')

    plt.show()


@Proxy.runInMainThread
def simulate_fourier_series(fn, period, N, dx=0.1):
    import matplotlib.pyplot as plt

    xs = np.arange(0, period, dx)
    ys = [fn(x) for x in xs]

    @lru_cache
    def dft(v):
        total = 0
        for x in xs:
            total += fn(x) * cmath.exp(-2j * cmath.pi / period * v * x) * dx
        return total / period

    # coefficients = [fourier_transform(lambda t: (0 if (t < 0 or t > period) else fn(t)), v) / period for v in range(-N, N+1)]
    # print(coefficients)

    def idft(t):
        return sum([dft(v) * cmath.exp(2j * cmath.pi / period * v * t) for v in range(-N, N+1)]).real

    _ys = [idft(x) for x in xs]

    # plot ys and _ys against xs
    plt.plot(xs, ys)
    plt.plot(xs, _ys, 'r')

    # get axis
    ax = plt.gca()
    ax.set_title(f'Fourier Series Approximate of N={N}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Signal Strength')

    plt.show()




if __name__ == '__main__':
    # simulate_discrete_fourier_transform(fn=lambda x: 1)
    simulate_fourier_series(lambda t: 1 if t > 0.5 else -1, 1, 10, 0.001)