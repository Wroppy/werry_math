from libraries.solver.nodes import *
from libraries.structures.formula import Formula


class Enthalpy(Formula):
    """
    Enthalpy describes the sum of the internal energy and the energy in creating the pressure of the system
    """
    description = {
        "H": ("The enthalpy of the system in Joules per Pascal per Meter Cubed", float),
        "U": ("The internal energy of the system in Joules", float),
        "P": ("The pressure of the system in Pascals", float),
        "V": ("The volume of the system in Meter Cubed", float)
    }

    def to_node(self) -> Equal:
        return Symbol("H") == Symbol("U") - Symbol("P") * Symbol("V")


class GibbsFreeEnergy(Formula):
    """
    Gibb's Free Energy is a measure of the amount of 'free' energy in a system that can do work
    This energy can drive endothermic reactions without external force or drive spontaneous reactions to not release energy
    If the Gibb's Free Energy is decreasing, the reaction will be spontaneous
    If the change is zero, the reaction is in equilibrium
    If the change is increasing, the reaction is non-spontaneous
    """
    description = {
        r"\Delta G": ("The change in Gibbs Free Energy in Joules", float),
        r"\Delta H": ("The change in enthalpy in Joules", float),
        "T": ("The temperature in Kelvin", float),
        r"\Delta S": ("The change in entropy in Joules per Kelvin", float)
    }

    def to_node(self) -> Equal:
        return Symbol(r"\Delta G") == Symbol(r"\Delta H") - Symbol("T") * Symbol(r"\Delta S")
