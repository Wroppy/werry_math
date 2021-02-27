from decimal import Decimal
import math
from typing import Union, Any

from utilities.markers import Marker

number = Any


@Marker.ignore_this
def match_or_raise(obj, type):
    if not isinstance(obj, type):
        raise NotImplementedError


class SNotation:
    mantissa: Decimal

    def __init__(self, mantissa: Union[str, Decimal], sigfig=None):
        if not isinstance(mantissa, Decimal):
            mantissa = Decimal(mantissa)
        self.mantissa = mantissa

        if sigfig is None:
            self.sigfig = SNotation.get_sigfig(str(mantissa))
        else:
            self.sigfig = sigfig
            self.mantissa = SNotation.round_sigfig(mantissa, self.sigfig)

    @staticmethod
    def get_decimal(mantissa: str):
        splited = mantissa.split('.')
        return 0 if len(splited) != 2 else len(splited[1])

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
    def round_sigfig(x: Decimal, n: int) -> Decimal:
        # https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
        return x if x == 0 else round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))

    def __mul__(self, other):
        match_or_raise(other, SNotation)

        return SNotation(self.mantissa * other.mantissa, min(self.sigfig, other.sigfig))

    def __truediv__(self, other):
        match_or_raise(other, SNotation)

        return SNotation(self.mantissa / other.mantissa, min(self.sigfig, other.sigfig))

    def __add__(self, other):
        match_or_raise(other, SNotation)

        dp = min(SNotation.get_decimal(str(self.mantissa)), SNotation.get_decimal(str(other.mantissa)))
        result = self.mantissa + other.mantissa
        sigfig = len(str(result).split('.')[0])+dp

        return SNotation(result, sigfig)

    def __sub__(self, other):
        match_or_raise(other, SNotation)

        return SNotation(self.mantissa - other.mantissa, min(self.sigfig, other.sigfig))

    def __pow__(self, power, modulo=None):
        match_or_raise(power, SNotation)

        return SNotation(self.mantissa ** power.mantissa, min(self.sigfig, power.sigfig))

    def __str__(self):
        mantissa = SNotation.round_sigfig(self.mantissa, self.sigfig)
        return str(mantissa)

    def __float__(self):
        return self.mantissa


# This is not yet good enough, a good thought though
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
        if not isinstance(power, float):
            raise NotImplementedError

        return UncertainNumber.from_relative(self.value ** power, self.relative_uncertainty() * power)

    def __str__(self):
        return f"{self.value} ± {self.uncertain}"


if __name__ == '__main__':
    n1 = SNotation("209.0", 4)
    n2 = SNotation("20.1", 4)

    u1 = UncertainNumber(SNotation("209.0"), SNotation("0.2"))
    u2 = UncertainNumber(SNotation("12"), SNotation("2.0"))
    print(u1 + u2)
    # print((n1 * n2).sigfig)
    # print((n1 * n2))
