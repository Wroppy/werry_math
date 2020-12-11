from libraries.solver.nodes.extension import *
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

