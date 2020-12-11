from libraries.solver.nodes import *


# https://medium.com/@mgarod/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
def add_method_to(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return None

    return decorator


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
    eq = Number(7) == Number(1) * ((Number(2) + Number(3) * Number(7)) / Number(2))
    eq.open_latex()
