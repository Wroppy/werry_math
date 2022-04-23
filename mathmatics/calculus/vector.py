import fnmatch
from typing import Callable


from mathmatics.structures.common import Range
from utilities.graphing import mpl_vector_field2

# Some terrible vector calculus stuff
def vector_field_plot(fn: Callable, xrange: Range, yrange: Range, dim: int = 2, *args, **kwargs):
    if dim == 2:
        mpl_vector_field2(fn, *xrange, *yrange, *args, **kwargs)
    else:
        raise Exception(f"Unsupported dimensions: {dim}")



def _love_diffeq(X, Y):
    w = 0.1
    return (
        -w * Y,
        w * X
    )


if __name__ == '__main__':
    vector_field_plot(_love_diffeq, Range(-10, 10), Range(-10, 10))