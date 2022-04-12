from typing import List, Any

from mathmatics.structures.common import MathObject


class Matrix(MathObject):
    """
    This is a matrix class, and i do not wish to write this myself
    """

    def __init__(self, data: List[List[Any]]):
        self.data = data

    def __setitem__(self, key, value: Any):
        if isinstance(key, int):
            self.data[key] = value
            return

        if not isinstance(key, tuple) or len(key) != 2:
            raise Exception("must only index matrices with 2-tuples")

        i, j = key
        self.data[i][j] = value

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) not in [1, 2]:
            raise Exception("must only index matrices with 2-tuples")

        if not isinstance(key, tuple):
            return self.data[key]

        i, j = key

        if isinstance(i, slice):
            items = self.data[i.start:i.stop:i.step]
            return [item[j] for item in items]
        else:
            items = self.data[i]
            return items[j]

    def swap_rows(self, i, j):
        old = self.data[i]
        self.data[i] = self.data[j]
        self.data[j] = old

    def rows(self):
        return len(self.data)

    def cols(self):
        return len(self.data[0])

    def is_square(self):
        return self.rows() == self.cols()

    def clone(self):
        return Matrix(self.data)

    def row_echelon(self, b):
        if self.cols() != len(b):
            raise Exception("matrix and vector must be same size")

        new_matrix = self.clone()
        rows = new_matrix.rows()
        i = 0

        for col in range(new_matrix.cols()):
            if i == rows:
                break

            # find pivot
            pivot = None
            for row in range(i, rows):
                if new_matrix[row, col] != 0:
                    pivot = row
                    break

                raise Exception(f"matrix does not contain pivot at (col, row) {col, row}")

            # swap rows
            if pivot != i:
                self.swap_rows(i, pivot)
                # swap b
                b[i], b[pivot] = b[pivot], b[i]

            # divide pivot row by pivot
            pivot_value = new_matrix[i, col]
            for j in range(new_matrix.cols()):
                new_matrix[i, j] /= pivot_value
            b[i] /= pivot_value

            # subtract from other rows
            for row in range(i, rows):
                if row == i:
                    continue

                factor = new_matrix[row, col]
                for j in range(new_matrix.cols()):
                    new_matrix[row, j] -= new_matrix[i, j] * factor

                b[row] -= b[i] * factor

            i += 1

        return new_matrix, b

    def row_reduce(self, b):
        if self.cols() != len(b):
            raise Exception("matrix and vector must be same size")

        new_matrix = self.clone()
        rows = new_matrix.rows()
        i = 0

        for col in range(new_matrix.cols()):
            if i == rows:
                break

            # find pivot
            pivot = None
            for row in range(i, rows):
                if new_matrix[row, col] != 0:
                    pivot = row
                    break

                raise Exception(f"matrix does not contain pivot at (col, row) {col, row}")

            # swap rows
            if pivot != i:
                self.swap_rows(i, pivot)
                # swap b
                b[i], b[pivot] = b[pivot], b[i]

            # divide pivot row by pivot
            pivot_value = new_matrix[i, col]
            for j in range(new_matrix.cols()):
                new_matrix[i, j] /= pivot_value
            b[i] /= pivot_value

            # subtract from other rows
            for row in range(rows):
                if row == i:
                    continue

                factor = new_matrix[row, col]
                for j in range(new_matrix.cols()):
                    new_matrix[row, j] -= new_matrix[i, j] * factor

                b[row] -= b[i] * factor

            i += 1

        return new_matrix, b

    def to_latex(self) -> str:
        out = "\\begin{matrix}"
        for row in self.data:
            out += " & ".join([str(item) for item in row])
            out += "\\\\"
        out += "\\end{matrix}"
        return out

    def __str__(self):
        out = ""

        for row in self.data:
            out += "| " + str(row)[1:-1] + " |\n"

        return out

    @staticmethod
    def identity(n):
        return Matrix(
            [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        )


if __name__ == '__main__':
    matrix = Matrix(
        [[1, 1, 1.6],
         [2, 5, -1],
         [2, 0, 1]]
    )
    # print(matrix[1, 1])
    # print(matrix)
    mat, b = matrix.row_reduce([5, 4, 2])
    print(mat)
    print(b)
