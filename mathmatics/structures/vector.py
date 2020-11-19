from mathmatics.exceptions.vector import VectorIndexOutOfBounds


class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __getitem__(self, location: int) -> float:
        try:
            return [self.x, self.y][location]
        except IndexError:
            raise VectorIndexOutOfBounds("Index out of bounds")

    def __str__(self):
        return f"Vector x: {self.x} y: {self.y}"

if __name__ == '__main__':
    vect = Vector2D(1, 2)
    print(vect[2])