from abc import ABC
from typing import Callable

from libraries.solver.nodes import Node, Operation, Number


class UnaryOperations(Operation, ABC):
    precedence = 3

    def __init__(self, left: Node):
        super().__init__(left, Number(0))
        self.left = left
        self.right = Number(0)


class Neg(UnaryOperations):
    def eval(self) -> float:
        return -self.left.eval()

    def to_latex(self) -> str:
        return f"-{self.left.to_latex()}"
