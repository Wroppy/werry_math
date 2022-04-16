import math
from typing import Union, List

V3 = List[float]
V2 = List[float]


def _angles_degrees(angle: V3):
    return list(map(lambda a: a / math.pi * 180, angle))


def _limit(value, low, high):
    return min(max(value, low), high)


def _dot_product(v1: V3, v2: V3):
    return sum([v1[i] * v2[i] for i in range(2)])


def _cross_product(v1: V3, v2: V3):
    return (Quaternions(0, *v1) * Quaternions(0, *v2)).vector()


def _norm_axis(v1: V2):
    a, b = v1
    return [a / (a * a + b * b), b / (a * a + b * b)]


class Quaternions:
    """
    Quaternions are 4-dimensional complex numbers.
    https://en.wikipedia.org/wiki/Quaternion

    They can represent 3D-rotations and orientations, this class will implement
    some important operations.
    https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation

    The coordinate system used is right-handed: +z upwards, +y into the page, +x to the right
    """

    _val: List[float]

    def __init__(self, w: float = 1, x: float = 0, y: float = 0, z: float = 0):
        self._val = [w, x, y, z]

    def scalar(self):
        return self._val[0]

    def vector(self):
        return self._val[1:]

    def __neg__(self):
        w, x, y, z = self
        return Quaternions(
            -w, -x, -y, -z
        )

    def __sub__(self, other: Union["Quaternions", float, int]):
        return self + -other

    def __add__(self, other: Union["Quaternions", float, int]):
        if isinstance(other, (float, int)):
            w, x, y, z = self
            return Quaternions(
                w + other,
                x + other,
                y + other,
                z + other
            )

        if isinstance(other, Quaternions):
            a1, b1, c1, d1 = self
            a2, b2, c2, d2 = other
            return Quaternions(
                a1 + a2,
                b1 + b2,
                c1 + c2,
                d1 + c2
            )

        raise TypeError("can only add a quaternion by a scaler or another quaternion")

    def __mul__(self, other: Union["Quaternions", float, int]):
        if isinstance(other, (float, int)):
            w, x, y, z = self
            return Quaternions(
                w * other,
                x * other,
                y * other,
                z * other
            )

        if isinstance(other, Quaternions):
            a1, b1, c1, d1 = self
            a2, b2, c2, d2 = other
            return Quaternions(
                a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2,
                a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
                a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2,
                a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2
            )

        raise TypeError("can only multiply a quaternion by a scaler or another quaternion")

    def __truediv__(self, other: Union[float, int]):
        if isinstance(other, (float, int)):
            w, x, y, z = self
            return Quaternions(
                w / other,
                x / other,
                y / other,
                z / other
            )

        # no division of other quaternions, because ambiguity of order

        raise TypeError("can only divide a quaternion by a scaler")

    def dot(self, other: "Quaternions"):
        if isinstance(other, Quaternions):
            a1, b1, c1, d1 = self
            a2, b2, c2, d2 = other
            return a1 * a2 + b1 * b2 + c1 * c2 + d1 * d2

        raise TypeError("can only dot a quaternion by another quaterion")

    def magnitude(self):
        return sum([a ** 2 for a in self._val])

    def unit(self):
        return self / self.magnitude()

    def conjugate(self):
        w, x, y, z = self
        return Quaternions(
            w,
            -x, -y, -z
        )

    def reciprocal(self):
        return self.conjugate() / self.magnitude() ** 2

    ### ROTATIONS ###
    def rotate(self, theta: float, unit: V3):
        """
        Returns the current rotation plus a rotation around the unit vector by angle theta, counter-clockwise

        :param theta: Rotation amount
        :param unit: Rotation direction
        :return:
        """
        return Quaternions.rotate_quaternion(theta, unit) * self

    @staticmethod
    def rotate_quaternion(theta: float, unit: V3):
        """
        Create a rotational quaternion from a unit vector and rotation angle theta

        :param theta: Rotation amount
        :param unit: Rotation direction
        :return:
        """
        # construct rotational quaterion
        ux, uy, uz = unit
        q = Quaternions(math.cos(theta / 2),
                        math.sin(theta / 2) * ux,
                        math.sin(theta / 2) * uy,
                        math.sin(theta / 2) * uz)

        return q

    def raw_rotate(self, point: V3):
        """
        Rotate a point by the current quaternion, returns the new point location

        :param point: Point to be rotated
        :return:
        """

        p = Quaternions(0, point[0], point[1], point[2])
        return self * p * self.conjugate()

    def facing(self, basis: V3) -> V3:
        """
        Returns the direction vector of the current orientation quaternion given a basis

        :param basis: A basis
        :return: The direction vector of the current orientation quaternion
        """
        return self.raw_rotate(basis).unit().vector()

    def euler_angles(self, basis: V3) -> V3:
        """
        Returns a list of (yaw, roll, pitch) directions given a orientational quaternion and a basis

        :param basis: The basis direction
        :return: The (yaw, roll, pitch) directions
        """
        # this is difficult
        # https://stackoverflow.com/questions/21622956/how-to-convert-direction-vector-to-euler-angles

        facing = self.facing(basis)
        up = self.UP(basis)

        x, y, z = facing
        w = basis
        U = _cross_product(w, facing)

        return [
            math.atan2(y, x),
            math.asin(z),
            math.atan2(_dot_product(w, up), _dot_product(U, up))
        ]

    def euler_angles_degrees(self, basis: V3):
        return _angles_degrees(self.euler_angles(basis))

    # collection of nice angles #
    def UP(self, basis: V3):
        q = Quaternions()
        q = q.rotate(math.pi / 2, [0, -1, 0])
        return q.raw_rotate(basis).vector()

    def FORWARD(self, basis: V3):
        return basis

    def __iter__(self):
        yield from self._val

    def __str__(self):
        w, x, y, z = self
        return f"({w} + {x}i + {y}j + {z}k)"

    def __repr__(self):
        w, x, y, z = self
        return f"Quaternion(w={w}, x={x}, y={y}, z={z})"


if __name__ == '__main__':
    basis = [1, 0, 0]
    q = Quaternions.rotate_quaternion(0, basis)
    print(f"Initial Angle {q.euler_angles_degrees(basis)}")

    print("Rotating")
    q = q.rotate(math.pi / 3, [0, 0, 1])
    print(f"Rotated Angle {q.euler_angles_degrees(basis)}")
