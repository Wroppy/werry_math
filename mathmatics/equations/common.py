from abc import ABC, abstractmethod
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np


class Equation(ABC):
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

        # set center
        plt.axhline(color='black', lw=0.5)
        plt.axvline(color='black', lw=0.5)

        # plot
        plt.plot(xs, ys)
        plt.show()


class CustomEquation(Equation):
    """
    A custom equation that takes in a generic function
    """

    def __init__(self, function: Callable):
        self.function = function

    def y(self, x: float) -> float:
        return self.function(x)

    def __str__(self):
        return f"y = function(x)"


if __name__ == '__main__':
    eq = CustomEquation(lambda x: x ** 2)
    eq.graph()