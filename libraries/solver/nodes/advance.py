import math
from abc import ABC

from libraries.solver.common import add_paren, add_brackets, add_square
from libraries.solver.nodes import Operation, Node, Number, Constant


class AdvanceOperations(Operation, ABC):
    pass


class Power(AdvanceOperations):
    precedence = 2

    def eval(self) -> float:
        return self.left.eval() ** self.right.eval()

    def to_latex(self) -> str:
        left = self.left.to_latex()
        if Operation.is_operation(self.left):
            left = add_paren(left)
        right = self.right.to_latex()
        if Operation.is_operation(self.right):
            right = add_brackets(right)

        return f"{left}^{right}"


class Root(AdvanceOperations):
    precedence = 2

    def eval(self) -> float:
        return self.left.eval() ** (1 / self.right.eval())

    def to_latex(self) -> str:
        left = self.left.to_latex()
        left = add_square(left)
        right = self.right.to_latex()
        right = add_brackets(right)

        return rf"\sqrt{left}{right}"


class Logarithm(AdvanceOperations):
    precedence = 2

    def eval(self) -> float:
        return math.log(self.right.eval(), self.left.eval())

    def to_latex(self) -> str:
        left = self.left.to_latex()
        left = add_brackets(left)
        right = self.right.to_latex()
        if Operation.is_operation(self.right):
            right = add_paren(right)
        right = add_brackets(right)

        return rf"\log_{left}{right}"


class NaturalLogarithm(Logarithm):
    def __init__(self, right: Node):
        super().__init__(Constant('e', math.e), right)

    def to_latex(self) -> str:
        right = self.right.to_latex()
        right = add_paren(right)
        return rf"\ln{right}"
