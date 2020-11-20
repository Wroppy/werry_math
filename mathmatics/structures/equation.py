from abc import ABC, abstractmethod
from typing import Callable, Union

import matplotlib.pyplot as plt
import numpy as np

from mathmatics.structures.common import MathObject


class Equation(MathObject, ABC):
    """
    An abstract base class for a generic equation that contains some helper methods
    """

    @abstractmethod
    def y(self, x: float) -> float:
        """
        Returns the y value for a given x

        :param x: The given x
        :return: The y value
        """
        pass

    def to_latex(self) -> Union[str, None]:
        return str(self)

    @abstractmethod
    def __str__(self):
        pass

    def print_y(self, x: float):
        print(self.y(x))

    def graph(self, start: float = -5, end: float = 10, steps: float = 0.01):
        """
        Graphs this equation

        :param start: Start x axis
        :param end: End x axis
        :param steps: Step to increase x by, larger indicts a more smooth graph
        :return: None
        """
        xs = np.arange(start, end, steps)
        ys = []
        for x in xs:
            ys.append(self.y(x))

        fig, ax = plt.subplots()
        # set center
        ax.axhline(color='black', lw=0.5)
        ax.axvline(color='black', lw=0.5)

        # plot
        ax.plot(xs, ys, 'b')
        plt.show()


class CustomEquation(Equation):
    """
    A custom equation that takes in a generic function
    """

    def __init__(self, function: Callable, latex: str = None):
        self.function = function
        self.latex = latex

    def y(self, x: float) -> float:
        return self.function(x)

    def to_latex(self) -> Union[str, None]:
        return self.latex

    def __str__(self):
        return f"y = function(x)"


if __name__ == '__main__':
    eq = CustomEquation(lambda x: 0.5 * x ** 2, "y=x^2")
    eq.open_in_desmos()
