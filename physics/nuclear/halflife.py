from libraries.solver.nodes import *
from libraries.structures.formula import Formula


class HalflifeFormula(Formula):
    """
    Radioactive element halflife calculator
    """
    description = {
        "t_{1/2}": ("Time for half of the elements to decay(halflife)", float),
        "t": ("Time elapsed", float),
        "N": ("Current atom population", float),
        "N_{0}": ("Initial atom population", float),
    }

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
    # f.describe('t_{1/2}')
    # print(f.solvefor('N_{0}'))
