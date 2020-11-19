from typing import List, Tuple

from mathmatics.exceptions.vector import VectorIndexOutOfBounds, VectorInterfaceInstance


class Vector:
    symbols = ["x", "y", "z"]

    def __init__(self, error=True):
        if error:
            raise VectorInterfaceInstance("cannot instance an interface")


class VectorND(Vector):
    def __init__(self, *values: float):
        super().__init__(error=False)
        self.values = [*values]

    @staticmethod
    def from_tuple(values: Tuple):
        return VectorND(*values)

    @staticmethod
    def from_list(values: List):
        return VectorND(*values)

    def __getitem__(self, location: int):
        try:
            return self.values[location]
        except IndexError:
            raise VectorIndexOutOfBounds("Index out of bounds")

    def x(self):
        try:
            return self.values[0]
        except IndexError:
            raise VectorIndexOutOfBounds("x out of bounds")

    def y(self):
        try:
            return self.values[1]
        except IndexError:
            raise VectorIndexOutOfBounds("y out of bounds")

    def z(self):
        try:
            return self.values[2]
        except IndexError:
            raise VectorIndexOutOfBounds("z out of bounds")

    def __str__(self):
        result = "Vector "
        for index, value in enumerate(self.values):
            if index in range(0, len(Vector.symbols)):
                result += f"{Vector.symbols[index]}: {value}"
            else:
                result += f"{index}: {value}"
            if index != len(self.values) - 1:
                result += ", "
        return result


class Vector2D(Vector):
    def __init__(self, x: float, y: float):
        super().__init__(error=False)
        self.x = x
        self.y = y

    def __getitem__(self, location: int) -> float:
        try:
            return [self.x, self.y][location]
        except IndexError:
            raise VectorIndexOutOfBounds("Index out of bounds")

    def __str__(self):
        return f"Vector x: {self.x}, y: {self.y}"


if __name__ == '__main__':
    vect = VectorND.from_tuple((1, 2, 3, 5))
    print(vect)
