import copy
from typing import Any, Optional, List, Dict

from libraries.solver.common import *
from libraries.solver.nodes import *
from libraries.solver.plugins import Plugin, BasicPlugin, AdvancePlugin


class MoreThanOneUnknown(Exception):
    def __init__(self):
        super(MoreThanOneUnknown, self).__init__("there is more than one unknowns")


class Solver:
    def __init__(self, equation: Equal, plugins: List[Plugin] = None):
        self.equation = equation

        if plugins is None:
            plugins = [BasicPlugin(), AdvancePlugin()]
        self.plugins = plugins

        # state
        self.state = {
            # number of missing symbols
            'number_missing': 0,
            # the missing symbol
            'missing_symbol': None,
            # -1 if missing symbol is on the left side, +1 on the right
            'missing_side': 0
        }

    def match_any(self, symbol_side: Node) -> Optional[Plugin]:
        if isinstance(symbol_side, Symbol):
            return None

        for plugin in self.plugins:
            if plugin.match(symbol_side):
                return plugin
        return None

    def solvewhere(self, symbols: Dict[str, float] = None, **kwargs) -> Optional[float]:
        # save & set state
        old_equation = copy.deepcopy(self.equation)
        self.state['number_missing'] = 0
        self.state['missing_side'] = UNDETERMINED

        # replace symbols with value
        if symbols is not None:
            self.replace_symbols(symbols)
        else:
            self.replace_symbols(kwargs)
        if self.state['number_missing'] > 1 or self.state['missing_symbol'] is None:
            self.equation = old_equation
            raise MoreThanOneUnknown()

        missing_side = self.state['missing_side']
        missing_symbol = self.state['missing_symbol']
        # put missing side on the left
        if missing_side == RIGHT_SIDE:
            tmp = self.equation.left
            self.equation.left = self.equation.right
            self.equation.right = tmp

        # balance
        plugin = self.match_any(self.equation.left)
        while plugin is not None:
            new_symbol_side, new_other_side = plugin.balance(missing_symbol, self.equation.left, self.equation.right)
            if new_symbol_side is None or new_other_side is None:
                break
            self.equation.left = new_symbol_side
            self.equation.right = new_other_side

            # else continue
            plugin = self.match_any(self.equation.left)

        if isinstance(self.equation.left, Symbol):
            result = self.equation.right.eval()
        else:
            result = None

        self.equation = old_equation
        return result

    def replace_symbols(self, symbols):
        def mod(_: Node, value: Any):
            if not isinstance(value, Symbol):
                return value

            if value.symbol in symbols:
                return Number(symbols[value.symbol])
            self.state['number_missing'] += 1
            self.state['missing_symbol'] = value.symbol
            return value

        def set_missing_side():
            if self.state['number_missing'] == 1:
                self.state['missing_side'] = LEFT_SIDE
            else:
                self.state['missing_side'] = RIGHT_SIDE

        self.equation.modify_w_callback(mod, set_missing_side)


if __name__ == '__main__':
    # equation = Equal(Symbol("F"), Multiplication(Symbol("m"), Multiplication(Addition(Number(1), Number(2)), Number(5))))
    # solver = Solver(equation, [BasicPlugin(), AdvancePlugin()])
    # print(equation.to_latex())
    # quit()
    # equation = Equal(
    #     Symbol("t_{1/2}"),
    #     Multiplication(
    #         Symbol("t"),
    #         Division(
    #             NaturalLogarithm(Number(2)),
    #             NaturalLogarithm(Division(Symbol("N_{0}"), Symbol("N")))
    #         )
    #     )
    # )
    equation = Equal(
        Symbol("x"),
        Addition(Number(1), Division(Number(1), Addition(Number(1), Multiplication(Addition(Number(1), Number(2)),
                                                                                   Addition(Number(1), Number(2))))))
    )
    # print(equation.to_latex())
    # solver = Solver(equation)
    # result = solver.solvewhere({
    #     "t_{1/2}": 12,
    #     "t": 56,
    #     "N": 1000
    # })
    # print(result)
