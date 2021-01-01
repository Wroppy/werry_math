from libraries.solver.nodes import *
from libraries.structures.formula import Formula


class QuadraticFormula(Formula):
    symbols = {'x', 'a', 'b', 'c'}

    def to_node(self) -> Equal:
        a = self.s('a')
        b = self.s('b')
        c = self.s('c')
        x = self.s('x')
        return x == PlusMinus(Neg(b), SquareRoot(b ** Number(2) - Number(4) * a * c)) / (Number(2) * a)


if __name__ == '__main__':
    eq = QuadraticFormula()
    print(eq.solvewhere(a=1, x=3, c=2))