from typing import Dict, List

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
        retVal = {}
        for k, v in self.content.items():
            retVal[k] = v * self.coefficient

        return retVal

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
        if index >= len(self.left) + len(self.right):
            return False

        if self.is_balanced():
            return True

        for i in range(1, limit):
            before = [*self.left, *self.right][index].coefficient
            [*self.left, *self.right][index].coefficient = i
            if self.balance(index + 1, limit):
                return True
            [*self.left, *self.right][index].coefficient = before

        return False

    @staticmethod
    def from_str(self, string: str) -> 'Equation':
        pass

    def __str__(self):
        lefts = [str(left) for left in self.left]
        rights = [str(right) for right in self.right]
        return f"{' + '.join(lefts)} = {' + '.join(rights)}"


if __name__ == '__main__':
    eq = Equation(
        [
            Molecule({"h": 2, "o": 2}),
            Molecule({"n": 2, "h": 4}),
        ],
        [
            Molecule({"n": 2}),
            Molecule({"h": 2, "o": 1}),
            Molecule({"o": 2}),
        ]
    )

    eq.balance()

    print(eq)
    print(eq.is_balanced())
    print(eq.counter)
