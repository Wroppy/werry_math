from abc import ABC, abstractmethod
from typing import Callable, Union

import matplotlib.pyplot as plt
import numpy as np
import sympy

from mathmatics.calculus.integral import integral
from mathmatics.calculus.derivative import derivative
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

    def derivative(self, x: float) -> float:
        """
        Calculates the derivative of this equation at x

        :param x: X
        :return: The derivative
        """
        return derivative(self.y, x)

    def integral(self, start: float, end: float) -> float:
        """
        Calculates the definite integral from start to end for this equation

        :param start: Start
        :param end: End
        :return: The definite integral
        """
        return integral(self.y, start, end)

    def to_latex(self) -> Union[str, None]:
        """
        Convert this equation to_latex

        :return:
        """
        return None

    def print_latex(self, **kwargs):
        """
        Prints the latex of the equation

        :return: None
        """
        latex = self.to_latex()
        if latex is None:
            print("LaTex not available for this equation")
        else:
            # todo: move this init to somewhere else
            sympy.init_printing()
            expr = sympy.sympify(latex)
            sympy.pprint(expr, use_unicode=True, **kwargs)

    def print_y(self, x: float):
        """
        Prints the equation evaluated at x

        :param x: X
        :return: None
        """
        print(self.y(x))

    def graph(self, start: float = -5, end: float = 10, steps: float = 0.01):
        """
        Graphs this equation from start to end

        :param start: Start x axis
        :param end: End x axis
        :param steps: Step to increase x by, larger indicts a more smooth graph
        :return: None
        """
        xs = np.arange(start, end, steps)
        ys = []
        for x in xs:
            try:
                ys.append(self.y(x))
            except Exception as e:
                print(str(e))
                ys.append(0)

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


if __name__ == '__main__':
    eq = CustomEquation(lambda x: 0.5 * x ** 2, "y=x^3")
    eq.graph()
