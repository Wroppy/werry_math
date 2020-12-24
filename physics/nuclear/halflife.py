from libraries.solver.nodes import *
from libraries.structures.formula import Formula


class Halflife(Formula):
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
        return Symbol("t_{1/2}") == Symbol("t") * (
                NaturalLogarithm(Number(2))
                /
                NaturalLogarithm(
                    Symbol("N_{0}")
                    /
                    Symbol("N")
                )
        )


if __name__ == '__main__':
    f = Halflife()
    print(f.solvewhere({
        "t": 521,
        "N": 312312,
        "N_{0}": 123
    }))
    # f.describe('t_{1/2}')
    # print(f.solvefor('N_{0}'))
