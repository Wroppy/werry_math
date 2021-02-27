import csv
from typing import Dict, List, Optional, Any
from decimal import Decimal

from physics.measurement.uncertainty import SNotation
from pathlib import Path

class Atom:
    default_path = "pt.csv"
    csv_element = "Symbol"
    default_resolver = {
        "u": "AtomicMass",
        "mass": "AtomicMass",
        "a": lambda info: Decimal(info["NumberofProtons"]) + Decimal(info["NumberofNeutrons"]),
        "z": "AtomicNumber",
        "period": "Period",
        "group": "Group",
        "phase": ("Phase", str),
        "type": ("Type", str),
        "ar": "AtomicRadius",
        "e": "Electronegativity",
        "ion": "FirstIonization",
        "p": "Density",
        "mp": "MeltingPoint",
        "bp": "BoilingPoint",
        "ele": ("Element", str)
    }

    contents: Any = None

    def __init__(self, element: str, path: str = None, resolver: Dict = None):
        if path is None:
            self.path = Atom.default_path
        if resolver is None:
            self.resolver = Atom.default_resolver

        if Atom.contents is None:
            Atom.contents = {}
            with open(Path(__file__).parent.absolute() / self.path) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Atom.contents[row[Atom.csv_element].lower()] = row
        try:
            self.info = Atom.contents[element.lower()]
        except IndexError:
            raise Exception(f"No Element named '{element}' found in the database")

        # setup default attributes
        for key, item in self.resolver.items():
            if callable(item):
                setattr(self, key, item(self.info))
                continue

            if isinstance(item, tuple):
                setattr(self, key, item[1](self.info[item[0]]))
                continue

            setattr(self, key, Decimal(self.info[item]))

    def select(self, attr: str):
        return self.info[attr]

    def __str__(self):
        return self.ele


class Molecule:
    def __init__(self, content: Dict[str, int], coeff: int = 1):
        self.content = content
        self.coefficient = coeff

    def molar_mass(self):
        mass = Decimal()
        for key, item in self.content.items():
            mass += Atom(key).u * item
        return mass

    def to_mols(self, grams):
        return Decimal(grams) / self.molar_mass()

    def to_grams(self, mols):
        return Decimal(mols) * self.molar_mass()


    def contents(self):
        ret_val = {}
        for k, v in self.content.items():
            ret_val[k] = v * self.coefficient

        return ret_val

    @staticmethod
    def from_str(string: str) -> Optional['Molecule']:
        coeff = 1
        content = {}

        strlen = len(string)
        index = 0

        while index < strlen and string[index].isdigit():
            coeff = int(string[index])
            index += 1

        if index >= strlen:
            return None

        if string[index] == '(':
            index += 1
            if index >= strlen:
                return None

        while index < strlen:
            c = string[index]
            if not (c.isalpha() and c.isupper()):
                break

            index += 1
            while index < strlen and string[index].isalpha() and string[index].islower():
                c += string[index]
                index += 1

            number = 0
            while index < strlen and string[index].isdigit():
                number = number * 10 + int(string[index])
                index += 1

            if number == 0:
                number = 1
            content[c] = number

        return Molecule(content, coeff)

    def __str__(self):
        l = []
        for k, v in self.content.items():
            l.append(f"{k.capitalize()}{v}")
        return f"{self.coefficient}({''.join(l)})"


if __name__ == '__main__':
    water = Molecule.from_str("H2O")
    print(SNotation(water.to_mols(12.3), 3))
