from typing import List

from utilities.markers import Proxy

def translate(value: float, left_min: float, left_max: float, right_min: float = 0, right_max: float = 1):
    """
    https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    """
    left_span = left_max - left_min
    right_span = right_max - right_min

    value_scaled = float(value - left_min) / float(left_span)

    return right_min + value_scaled * right_span
