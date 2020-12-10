import math
from abc import ABC

from common.solver.nodes import Operation


class AdvanceOperations(Operation, ABC):
    pass


class Power(AdvanceOperations):
    def eval(self) -> float:
        return self.left.eval() ** self.right.eval()


class Root(AdvanceOperations):
    def eval(self) -> float:
        return self.left.eval() ** (1 / self.right.eval())


class Logarithm(AdvanceOperations):
    def eval(self) -> float:
        return math.log(self.right.eval(), self.left.eval())
