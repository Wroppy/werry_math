from chemistry.constants import R
from libraries.solver.nodes import *
from libraries.structures.formula import Formula


class IdealGasLaw(Formula):
    """
    The Ideal Gas Law modeling the behaviors of ideal gases
    """
    description = {
        "P": ("Pressure in pascals", float),
        "V": ("Volume in liters", float),
        "n": ("Number of atoms in mols", float),
        "T": ("Temperature in kelvin", float)
    }

    def to_node(self) -> Equal:
        return Equal(
            Multiplication(Symbol("P"), Symbol("V")),
            Multiplication(Symbol("n"), Multiplication(Constant("R", R), Symbol("T")))
        )


class RealGasLaw(Formula):
    """
    The Real Gas Law correcting the Ideal Gas Law and accurately models real gases
    """
    description = {
        "P": ("Pressure in pascals", float),
        "V": ("Volume in liters", float),
        "n": ("Number of atoms in mols", float),
        "T": ("Temperature in kelvin", float),
        "a": ("Constant regarding to the type of gas", float),
        "b": ("Constant regarding to the type of gas", float)
    }

    def to_node(self) -> Equal:
        return Equal(
            Multiplication(
                Addition(
                    Symbol("P"),
                    Division(
                        Multiplication(
                            Power(Symbol("n"), Number(2)),
                            Symbol("a")
                        ),
                        Power(Symbol("V"), Number(2))
                    )
                ),
                Subtraction(
                    Symbol("V"),
                    Multiplication(Symbol("n"), Symbol("b"))
                )
            ),
            Multiplication(
                Symbol("n"),
                Multiplication(
                    Constant("R", R),
                    Symbol("T")
                )
            )
        )


class EffusionLaw(Formula):
    """
    Graham's Law of Effusion describes the rate of effusion of two elements in the same environment
    It states the ratio between the rate of effusion equals the square root of the inverse ratio of its molar masses
    """
    description = {
        "r_{a}": ("Rate of effusion of gas a", float),
        "r_{b}": ("Rate of effusion of gas b", float),
        "M_{a}": ("Molar Mass of gas b", float),
        "M_{b}": ("Molar Mass of gas b", float),
    }

    def to_node(self) -> Equal:
        return Equal(
            Division(
                Symbol("r_{a}"),
                Symbol("r_{b}")
            ),
            SquareRoot(
                Division(
                    Symbol("M_{b}"),
                    Symbol("M_{a}"),
                )
            )
        )


if __name__ == '__main__':
    law = EffusionLaw()
    print(law.solvewhere({
        "r_{a}": 12,
        "r_{b}": 5,
        "M_{b}": 6
    }))
    # law.open_latex()