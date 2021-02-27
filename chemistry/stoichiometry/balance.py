from typing import List

from chemistry.stoichiometry.atoms import Molecule
from utilities.markers import Marker


@Marker.ignore_this
def merge_content(d1, d2):
    for k, v in d2.items():
        if k in d1:
            d1[k] += v
        else:
            d1[k] = v
    return d1


@Marker.ignore_this
def is_the_same(d1, d2) -> bool:
    for k, v in d1.items():
        if k not in d2:
            return False
        if v != d2[k]:
            return False

    return True



class Equation:
    counter: int

    def __init__(self, left: List[Molecule], right: List[Molecule]):
        self.left = left
        self.right = right
        self.counter = 0

    def is_balanced(self) -> bool:
        left_dict = {}
        for molecule in self.left:
            left_dict = merge_content(left_dict, molecule.contents())

        right_dict = {}
        for molecule in self.right:
            right_dict = merge_content(right_dict, molecule.contents())

        return is_the_same(left_dict, right_dict)

    def balance(self, index: int = 0, limit: int = 21):
        self.counter += 1
        # check even if index is out, as it might be the last balance
        if self.is_balanced():
            return True

        if index >= len(self.left) + len(self.right):
            return False

        for i in range(2, limit):
            before = [*self.left, *self.right][index].coefficient
            [*self.left, *self.right][index].coefficient = i
            if self.balance(index + 1, limit):
                return True
            [*self.left, *self.right][index].coefficient = before

        return False

    @staticmethod
    def from_str(string: str) -> 'Equation':
        left, right = string.split('=')
        lefts = left.split('+')
        rights = right.split('+')

        left_molecules = []
        right_molecules = []

        for left in lefts:
            result = Molecule.from_str(left)
            if result is None:
                raise Exception(f"cannot parse '{left}' in input")
            left_molecules.append(result)
        for right in rights:
            result = Molecule.from_str(right)
            if result is None:
                raise Exception(f"cannot parse '{right}' in input")
            right_molecules.append(result)

        return Equation(left_molecules, right_molecules)

    def __str__(self):
        lefts = [str(left) for left in self.left]
        rights = [str(right) for right in self.right]
        return f"{' + '.join(lefts)} = {' + '.join(rights)}"


if __name__ == '__main__':
    eq = Equation.from_str("C8H18+O2=CO2+H2O")
    print(eq)

    eq.balance(limit=26)

    print(eq)
    print(eq.is_balanced())
    print(eq.counter)