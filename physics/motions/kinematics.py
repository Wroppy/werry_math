from libraries.solver.nodes import Equal, Division, Number
from libraries.structures.formula import Formula


class MotionV(Formula):
    symbols = ["v", "u", "a", "t"]

    def to_node(self) -> Equal:
        return self.s("v") == self.s("u") + self.s("a") * self.s("t")


class MotionSA(Formula):
    symbols = ["s", "u", "t", "a"]

    def to_node(self) -> Equal:
        return self.s("s") == self.s("u") * self.s("t") + (Number(1) / Number(2)) * self.s("a") * self.s("t") ** 2


class MotionVSqrt(Formula):
    symbols = ["v", "u", "a", "s"]

    def to_node(self) -> Equal:
        return self.s("v") ** 2 == self.s("u") ** 2 + Number(2) * self.s("a") * self.s("s")


class MotionSV(Formula):
    symbols = ["s", "v", "u", "t"]

    def to_node(self) -> Equal:
        return self.s("s") == (self.s("v") - self.s("u")) / 2 * self.s("t")
