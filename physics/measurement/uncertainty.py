import math
from cmath import log10
from math import floor

from utilities.markers import Marker

number = float


@Marker.ignore_this
def match_or_raise(obj, type):
    if not isinstance(obj, type):
        raise NotImplementedError


class SNotation:
    mantissa: str

    def __init__(self, mantissa: str, power: int = 0, sigfig=None):
        self.mantissa = mantissa
        self.power = power
        if sigfig is None:
            self.sigfig = SNotation.get_sigfig(mantissa)
        else:
            self.sigfig = sigfig
            self.mantissa = str(SNotation.round_sigfig(float(self.mantissa), self.sigfig))

    @staticmethod
    def get_sigfig(mantissa: str) -> int:
        if '.' in mantissa:
            mantissa = mantissa.replace('.', '')

        mi = 0
        mlen = len(mantissa)
        sigfig = 0

        if mi >= mlen:
            return -1

        while mantissa[mi] == '0':
            mi += 1
            if mi >= mlen:
                return -1
        while mi < mlen:
            sigfig += 1
            mi += 1
        return sigfig

    @staticmethod
    def round_sigfig(x: float, n: int) -> float:
        # TODO: Make it a bit better
        # https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
        return x if x == 0 else round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))

    def __str__(self):
        out = f"{self.mantissa}"
        if self.power != 0:
            out += f"x10^{self.power}"
        return out

    def __mul__(self, other):
        match_or_raise(other, SNotation)

        result = float(self.mantissa) * float(other.mantissa)
        return SNotation(str(result), self.power + other.power, min(self.sigfig, other.sigfig))


class UncertainNumber:
    def __init__(self, value: number, uncertain: number):
        self.value = value
        self.uncertain = uncertain

    @staticmethod
    def from_absolute(value: number, abs_uncertain: number):
        return UncertainNumber(value, abs_uncertain)

    @staticmethod
    def from_relative(value: number, rel_uncertain: number):
        return UncertainNumber(value, rel_uncertain * value)

    def absolute_uncertainty(self):
        return self.uncertain

    def relative_uncertainty(self):
        return self.uncertain / self.value

    def __add__(self, other):
        if not isinstance(other, UncertainNumber):
            raise NotImplementedError

        return UncertainNumber(self.value + other.value, self.absolute_uncertainty() + other.absolute_uncertainty())

    def __sub__(self, other):
        if not isinstance(other, UncertainNumber):
            raise NotImplementedError

        return UncertainNumber(self.value - other.value, self.absolute_uncertainty() + other.absolute_uncertainty())

    def __mul__(self, other):
        if not isinstance(other, UncertainNumber):
            raise NotImplementedError

        return UncertainNumber.from_relative(self.value * other.value,
                                             self.relative_uncertainty() + other.relative_uncertainty())

    def __truediv__(self, other):
        if not isinstance(other, UncertainNumber):
            raise NotImplementedError

        return UncertainNumber.from_relative(self.value / other.value,
                                             self.relative_uncertainty() + other.relative_uncertainty())

    def __pow__(self, power, modulo=None):
        if not isinstance(power, number):
            raise NotImplementedError

        return UncertainNumber.from_relative(self.value ** power, self.relative_uncertainty() * power)

    def __str__(self):
        return f"{self.value} +- {self.uncertain}"


if __name__ == '__main__':
    n1 = SNotation("209.0", 0, 3)
    n2 = SNotation("20.1", 0, 3)
    print(n1.sigfig)
    print((n1 * n2).sigfig)
