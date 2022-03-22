from typing import List, Tuple
import cmath
import random

_inv_root2 = 1 / cmath.sqrt(2)
_root2 = cmath.sqrt(2)
bra = List[complex]
ket = List[complex]


def vdot(v1, v2):
    return sum(v1[i] * v2[i] for i in range(len(v1)))


def vinv(v):
    return [-x for x in v]


def qdot(q1: ket, q2: ket) -> complex:
    return sum([q1[i].conjugate() * q2[i] for i in range(len(q1))])


def qmag(q1: ket, q2: ket) -> complex:
    return qdot(q1, q2) * qdot(q2, q1)


def qbra(q1: ket) -> bra:
    return [q.conjugate() for q in q1]


def qbasis(a: complex, b: complex, basis_a: ket, basis_b: ket) -> ket:
    return [a * q1 + b * q2 for q1, q2 in zip(basis_a, basis_b)]


class QSpin:
    # static variables
    _spin_states = {
        'up': [1, 0],
        'down': [0, 1],
        'right': qbasis(_inv_root2, _inv_root2, [1, 0], [0, 1]),
        'left': qbasis(_inv_root2, -_inv_root2, [1, 0], [0, 1]),
        'in': qbasis(_inv_root2, 1j * _inv_root2, [1, 0], [0, 1]),
        'out': qbasis(_inv_root2, -1j * _inv_root2, [1, 0], [0, 1]),
    }

    spin_state_type = Tuple[complex, complex]
    spin_coords_type = Tuple[float, float, float]

    def __init__(self):
        self.state = QSpin._spin_states['up']

    def set_state(self, new_state: spin_state_type):
        self.state = new_state

    @staticmethod
    def coords_to_state(coords: spin_coords_type):
        x, y, z = coords
        cu = z + _inv_root2 * y + _inv_root2 * x
        cd = _inv_root2 * x + 1j * _inv_root2 * y
        return cu, cd

    @staticmethod
    def state_to_coords(state: spin_state_type):
        cu = qdot(QSpin._spin_states['up'], state)
        cd = qdot(QSpin._spin_states['down'], state)

        y = cd.imag * _root2
        x = cd.real * _root2
        z = cu.real - _inv_root2 * y - _inv_root2 * x

        return x.real, y.real, z.real

    def set_state_with_coords(self, coords: spin_coords_type):
        cu, cd = QSpin.coords_to_state(coords)
        self.state = [cu, cd]

    def state_as_coords(self):
        return QSpin.state_to_coords(self.state)

    def measure_spin(self, coords: spin_coords_type):
        if coords[0] ** 2 + coords[1] ** 2 + coords[2] ** 2 != 1:
            raise ValueError('Spin coordinates must be of unit length')

        # get the angle between the current spin state and the desired spin state
        angle = cmath.acos(vdot(self.state_as_coords(), coords))

        # the probability of measuring +1
        p1 = cmath.cos(0.5 * angle).real ** 2
        # pn1 = cmath.sin(0.5 * angle).real ** 2

        if random.random() < p1:
            # if +1, set state to +1
            self.set_state(QSpin.coords_to_state(coords))
            return 1
        else:
            # else, set state to -1
            self.set_state(QSpin.coords_to_state(vinv(coords)))
            return -1


if __name__ == '__main__':
    spin = QSpin()

    # print(QSpin._spin_states['up'])
    # print(QSpin._spin_states['right'])
    # print(qmag(QSpin._spin_states['up'], QSpin._spin_states['right']))
    print("initial state")
    print(spin.state_as_coords())
    print(spin.measure_spin([1, 0, 0]))
    print(spin.measure_spin([1, 0, 0]))
    print(spin.measure_spin([1, 0, 0]))
    print(spin.measure_spin([1, 0, 0]))
    print(spin.measure_spin([1, 0, 0]))
    print(spin.measure_spin([1, 0, 0]))
    print("final state")
    print(spin.state_as_coords())
