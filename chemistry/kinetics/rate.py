from libraries.solver.nodes.extension import *
from libraries.structures.formula import Formula


class ReactionRate(Formula):
    """
    The formula to determine the rate of a reaction
    The order/degree of reaction is the sum of n and m
    """
    description = {
        "rate": "The reaction rate",
        "k": "Reaction constant",
        "[A]": "Concentration of reactant A",
        "n": "Reaction constant",
        "[B]": "Concentration of reactant B",
        "m": "Reaction constant",
    }

    def to_node(self) -> Equal:
        return Symbol("rate") == Symbol("k") * Symbol("[A]") ** Symbol("n") * Symbol("[B]") ** Symbol("m")


class EquilibriumConstant(Formula):
    def to_node(self) -> Equal:
        return Symbol("K_c") == (Symbol("[C]") ** Symbol("c") * Symbol("[D]") ** Symbol("d")) / (Symbol("[A]") ** Symbol("a") * Symbol("[B]") ** Symbol("b"))


if __name__ == '__main__':
    rate = EquilibriumConstant()
    rate.open_latex()

