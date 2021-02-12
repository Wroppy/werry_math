from typing import Dict, List, Optional

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


class Molecule:
    def __init__(self, content: Dict[str, int], coeff: int = 1):
        self.content = content
        self.coefficient = coeff

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
    eq = Equation.from_str("PbN2O6+NaCl=PbCl2+NaNO3")
    print(eq)

    eq.balance()

    print(eq)
    print(eq.is_balanced())
    print(eq.counter)
