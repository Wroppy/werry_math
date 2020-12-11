from libraries.solver.nodes import *
from libraries.solver.nodes.extension import *
from libraries.structures.formula import Formula


class FirstLaw(Formula):
    """
    The First Law of Thermodynamics
    It states that the change in internal energy is equal to the energy done to the system as heat minus the work done by the system
    """
    description = {
        r"\Delta U": ("Change in internal energy in Joules", float),
        "Q": ("Energy supplied to the system as heat in Joules", float),
        "W": ("Work done by the system in Joules", float)
    }

    def to_node(self) -> Equal:
        return Symbol(r"\Delta U") == Symbol("Q") - Symbol("W")


class SpecificHeatCapacity(Formula):
    """
    Formula including the Specific Heat Capacity
    It states the energy as heat gained by the system equals the mass times the SHC times the change in temperature
    """
    description = {
        "Q": ("The energy - as heat - gained by the system in Joules", float),
        "m": ("The mass of the system in Kilograms", float),
        "c": ("The specific heat capacity of the system in Joules per Kelvin per Kilogram", float),
        r"\Delta T": ("The change in temperature in Kelvin", float)
    }

    def to_node(self) -> Equal:
        return Symbol("Q") == Symbol("m") * Symbol("c") * Symbol(r"\Delta T")


class HessLaw(Formula):
    latex_only = True
    """
    Hess's law states that the change in enthalpy is path-independent
    Meaning we can directly compare the enthalpy between the start and the final form
    """
    def to_node(self) -> Equal:
        return Symbol(r"\Delta H_{reaction}") == \
               Sum(Sub(Symbol("n_p")*Symbol("H_f"), String('products'))) \
               - Sum(Sub(Symbol("n_r")*Symbol("H_f"), String('reactants')))

if __name__ == '__main__':
    # law = SpecificHeatCapacity()
    # law.open_latex()
    # print(law.solvewhere(Q=12, m=5, c=16))
    eq = HessLaw()
    print(eq.to_latex())
    eq.open_latex()