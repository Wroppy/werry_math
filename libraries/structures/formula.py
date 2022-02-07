from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Callable, Any, Union, Optional, Set

from libraries.solver.nodes import Equal, Symbol
from libraries.solver.solver import Solver
from utilities.latex import open_latex
import sympy
import unicodeit


class LatexOnlyFormula(Exception):
    def __init__(self):
        super(LatexOnlyFormula, self).__init__("cannot solve for latex only formulas")


class SymbolNotFound(Exception):
    pass


def format_type(ty: type) -> str:
    if ty == int:
        return 'int'
    if ty == float:
        return 'float'
    return str(ty)


class Formula(ABC):
    description: Dict[str, Union[str, Tuple[str, type]]]
    latex_only: bool
    symbols: List[str]
    __symbols: List[Symbol]

    def __init__(self):
        self.__symbols = []

        if hasattr(self, 'symbols'):
            self.description = {}
            for key in self.symbols:
                self.description[key] = key
        if hasattr(self, 'description'):
            for key in self.description:
                self.__symbols.append(Symbol(key))
        # here to assert it wont crash
        self.to_node()

    @abstractmethod
    def to_node(self) -> Equal:
        pass

    def s(self, key: str) -> Symbol:
        """
        Finds the symbol 'key' in this formula

        :param key: The symbol to find
        :return: The Symbol Node
        """
        for sym in self.__symbols:
            if sym.symbol == key:
                return sym
        raise SymbolNotFound(f"symbol '{key}' does not exist in {self.symbols}")

    def explain(self, unicode: bool = False):
        name = self.__class__.__name__

        doc = self.__doc__
        if doc is None:
            cleaned_doc = "None"
        else:
            cleaned_doc = []
            for line in doc.split('\n'):
                if len(line.strip()) == 0:
                    continue
                cleaned_doc.append(line.strip())
            cleaned_doc = '\n'.join(cleaned_doc)

        if hasattr(self, 'description'):
            max_symbol_length = len(max(self.description.keys(), key=lambda k: len(k)))
            max_type_length = 0
            if len(self.description) > 0:
                for key in self.description:
                    value = self.description[key]
                    if isinstance(value, str):
                        continue
                    max_type_length = max(max_type_length, len(format_type(value[1])))
            symbols = []
            for symbol in self.description:
                data = self.description[symbol]
                if unicode:
                    symbol = unicodeit.replace(symbol)
                padded_symbol = symbol + ' ' * (max_symbol_length - len(symbol))
                message = f"{padded_symbol}: "
                if isinstance(data, str):
                    message += ' ' * (max_type_length + 3) + data
                else:
                    padded_type = format_type(data[1]) + ' ' * (max_type_length - len(format_type(data[1])))
                    message += f"[{padded_type}] {data[0]}"
                symbols.append(message)
            symbols = '\n'.join(symbols)
        else:
            symbols = 'None'

        result = f"""{'-' * 20}
description for '{name}':
{cleaned_doc}
symbols:
{symbols}
{'-' * 20}"""
        print(result)

    def to_latex(self) -> str:
        return self.to_node().to_latex()

    def open_latex(self):
        latex = self.to_latex()
        if latex is None:
            print("LaTex not available for this equation")
            return
        open_latex(latex)

    def print_latex(self):
        from IPython.display import Math, display
        latex = self.to_latex()
        sympy.init_printing(use_unicode=True)
        expr = Math(latex)
        # expr = sympy.sympify(latex, evaluate=False)
        display(expr)
        # sympy.pprint(expr)

    def is_latex_only(self):
        return hasattr(self, "latex_only")

    def solvewhere(self, symbols: Dict[str, Any] = None, **kwargs: Any) -> float:
        if self.is_latex_only():
            raise LatexOnlyFormula

        solver = Solver(self.to_node())
        return solver.solvewhere(symbols, **kwargs)

    def solvefor(self, symbol: str):
        return self.solve(symbol)

    def solve(self, symbol: str = None):
        print(f"Solving for '{self.__class__.__name__}'")
        args = {}
        for key in self.description:
            if key == symbol:
                continue
            desc = self.description[key]
            result = input(f"{key}: ")
            if len(result) == 0:
                continue
            try:
                result = float(result)
            except:
                pass
            args[key] = result
        return self.solvewhere(symbols=args)


if __name__ == '__main__':
    pass
