from abc import ABC, abstractmethod

from physics.structures.common import PhysicsObject


class Formula(PhysicsObject, ABC):
    def __init__(self):
        pass

    @abstractmethod
    def solve(self):
        # TODO, create solve method
        pass
