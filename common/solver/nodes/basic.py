from abc import ABC

from common.solver.nodes import Operation


class BasicOperations(Operation, ABC):
    pass


class Multiplication(BasicOperations):
    def eval(self) -> float:
        return self.left.eval() * self.right.eval()


class Division(BasicOperations):
    def eval(self) -> float:
        return self.left.eval() / self.right.eval()


class Addition(BasicOperations):

    def eval(self) -> float:
        return self.left.eval() + self.right.eval()


class Subtraction(BasicOperations):

    def eval(self) -> float:
        return self.left.eval() + self.right.eval()
