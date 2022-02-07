from decimal import Decimal

from libraries.solver.nodes import *
from libraries.structures.formula import Formula


class CoulombsLaw(Formula):
    description = {
        "F": "the electric force on the charges",
        "q_1": "the charge of the first charge in Coulombs",
        "q_2": "the charge of the second charge in Coulombs",
        "r": "the distance between the charges in meters",
    }

    def to_node(self) -> Equal:
        return Symbol("F") == Constant("k", Decimal("8.99e9")) * (Symbol("q_1") * Symbol("q_2")) / Symbol("r")**Number(2)