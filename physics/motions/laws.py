from libraries.solver.nodes import *
from libraries.structures.formula import Formula

class SecondLaw(Formula):

    """
    Newton's second law of motion
    https://en.wikipedia.org/wiki/Newton%27s_laws_of_motion
    """

    description = {
        "F": "force",
        "m": "mass",
        "a": "acceleration"
    }
    def to_node(self) -> Equal:
        return Symbol("F") == Symbol("m") * Symbol("a")

if __name__ == '__main__':
    law = SecondLaw()
    law.explain()
    print(law.solvewhere(F=10, m=1, a=10))