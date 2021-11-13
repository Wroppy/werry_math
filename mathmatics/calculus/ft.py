import cmath


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
        total += F(x) * cmath.exp(2j * cmath.pi * x * t)
        x += 0.1

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
        total += f(x) * cmath.exp(-2j * cmath.pi * v * x)
        x += 0.1

    return total
