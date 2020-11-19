from abc import ABC, abstractmethod
from typing import List, Tuple

from mathmatics.exceptions.vector import VectorIndexOutOfBounds


class Vector(ABC):
    """
    Generic vector class
    """
    symbols = ["x", "y", "z", "w"]

    @abstractmethod
    def __getitem__(self, location: int):
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def __str__(self):
        pass


class VectorND(Vector):
    """
    An n-dimensional vector
    """
    def __init__(self, *values: float):
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
            raise VectorIndexOutOfBounds("index out of bounds")

    def size(self) -> int:
        return len(self.values)

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
    """
    A two-dimensional vector
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __getitem__(self, location: int) -> float:
        try:
            return [self.x, self.y][location]
        except IndexError:
            raise VectorIndexOutOfBounds("index out of bounds")

    def size(self) -> int:
        return 2

    def __str__(self):
        return f"Vector x: {self.x}, y: {self.y}"


if __name__ == '__main__':
    vect = VectorND.from_tuple((1, 2, 3, 5))
    print(vect)
