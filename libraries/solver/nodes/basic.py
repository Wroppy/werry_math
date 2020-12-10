from abc import ABC

from libraries.solver.common import add_paren, add_brackets
from libraries.solver.nodes import Operation, Symbol


class BasicOperations(Operation, ABC):
    operator: str

    def to_latex(self) -> str:
        left = self.left.to_latex()
        if Operation.is_operation(self.left) and self.left.precedence < self.precedence:
            left = add_paren(left)
        right = self.right.to_latex()
        if Operation.is_operation(self.right) and self.precedence > self.right.precedence:
            right = add_paren(right)
        return f"{left}{self.operator}{right}"


class Multiplication(BasicOperations):
    precedence = 1
    operator = '*'

    def eval(self) -> float:
        return self.left.eval() * self.right.eval()

    def to_latex(self) -> str:
        left = self.left.to_latex()
        if Operation.is_operation(self.left) and self.left.precedence < self.precedence:
            left = add_paren(left)
        right = self.right.to_latex()
        if Operation.is_operation(self.right) and self.precedence > self.right.precedence:
            right = add_paren(right)

        if isinstance(self.left, Symbol) or isinstance(self.right, Symbol) or Operation.is_operation(
                self.right) or Operation.is_operation(self.left):
            return f"{left}{right}"

        return f"{left}*{right}"


class Division(BasicOperations):
    precedence = 1
    operator = '/'

    def eval(self) -> float:
        return self.left.eval() / self.right.eval()

    def to_latex(self) -> str:
        left = self.left.to_latex()
        left = add_brackets(left)
        right = self.right.to_latex()
        right = add_brackets(right)
        return rf"\frac{left}{right}"


class Addition(BasicOperations):
    precedence = 0
    operator = '+'

    def eval(self) -> float:
        return self.left.eval() + self.right.eval()


class Subtraction(BasicOperations):
    precedence = 0
    operator = '-'

    def eval(self) -> float:
        return self.left.eval() + self.right.eval()
