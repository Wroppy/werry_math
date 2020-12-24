from gui.common import add_method_to
from libraries.solver.nodes.advance import Power
from libraries.solver.nodes.basic import Division, Addition, Subtraction, Multiplication
from libraries.solver.nodes.node import Node, Equal


@add_method_to(Node)
def __add__(self, other):
    return Addition(self, other)


@add_method_to(Node)
def __sub__(self, other):
    return Subtraction(self, other)


@add_method_to(Node)
def __mul__(self, other):
    return Multiplication(self, other)


@add_method_to(Node)
def __truediv__(self, other):
    return Division(self, other)


@add_method_to(Node)
def __pow__(self, other):
    return Power(self, other)


@add_method_to(Node)
def __eq__(self, other):
    return Equal(self, other)


if __name__ == '__main__':
    # eq = Number(7) == Number(1) * ((Number(2) + Number(3) * Number(7)) / Number(2))
    # eq.open   _latex()
    pass
