from libraries.solver.nodes import *
from libraries.structures.formula import Formula, create_solver


class HalflifeFormula(Formula):
    symbols = ['t', 't_{1/2}', 'N_{0}', 'N']

    def __init__(self):
        self.solvers = {
            't_{1/2}': create_solver(HalflifeFormula.solve_halflife),
            'N_{0}': create_solver(HalflifeFormula.solve_N0),
            'N': create_solver(HalflifeFormula.solve_N),
            't': create_solver(HalflifeFormula.solve_t),
        }

    @staticmethod
    def solve_halflife(t: float, N0: float, N: float) -> float:
        return t * (math.log(2) / math.log(N0 / N))

    @staticmethod
    def solve_N0(N: float, t12: float, t: float) -> float:
        return N * 2 ** (t / t12)

    @staticmethod
    def solve_t(t12: float, N0: float, N: float) -> float:
        return t12 * math.log(N0 / N) / math.log(2)

    @staticmethod
    def solve_N(N0: float, t12: float, t: float) -> float:
        return N0 / 2 ** (t / t12)

    def to_latex(self) -> str:
        return r"t_{1/2}=t\frac{\ln(2)}{\ln(\frac{N_{0}}{N})}"

    def to_node(self) -> Equal:
        return Equal(
            Symbol("t_{1/2}"),
            Multiplication(
                Symbol("t"),
                Division(
                    NaturalLogarithm(Number(2)),
                    NaturalLogarithm(Division(Symbol("N_{0}"), Symbol("N")))
                )
            )
        )


if __name__ == '__main__':
    f = HalflifeFormula()
    f.describe('t_{1/2}')
    print(f.solvefor('N_{0}'))
