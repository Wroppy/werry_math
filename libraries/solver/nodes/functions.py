import copy

from libraries.solver.common import add_brackets
from libraries.solver.nodes import Operation, Function, Node, Number, Equal


class CannotEvalPureFunctions(Exception):
    pass

class Sum(Function):
    def __init__(self, function: Node, start: Equal = None, end: Node = None):
        super().__init__()
        self.function = function
        self.start = start
        self.end = end
        if start is None or end is None:
            self.pure = True
            self.parameters = [function]
        else:
            self.pure = False
            self.parameters = [start, end, function]

    def eval(self) -> float:
        if self.pure:
            raise CannotEvalPureFunctions

        total = 0
        start = int(self.start.right.eval())
        end = int(self.end.eval())
        for node in range(start, end + 1):
            func = Function.replace_symbols(self.start.left.symbol, self.function)
            total += func.eval()
        return total

    def to_latex(self) -> str:
        base = r"\sum"
        func = self.function.to_latex()
        if not self.pure:
            start = add_brackets(self.start.to_latex())
            end = add_brackets(self.end.to_latex())
            return base + rf"_{start}^{end}{func}"

        if self.start:
            start = add_brackets(self.start.to_latex())
            base += rf"_{start}"
        if self.end:
            end = add_brackets(self.end.to_latex())
            base += rf"^{end}"
        if self.start is None and self.end is None:
            base += " "
        return base + func


# if __name__ == '__main__':
    # sig = Sum()