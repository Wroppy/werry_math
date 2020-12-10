from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Callable, Any, Union, Optional

from libraries.solver.nodes import Equal
from libraries.solver.solver import Solver
from utils.latex import open_latex

def format_type(ty: type) -> str:
    if ty == int:
        return 'int'
    if ty == float:
        return 'float'
    return str(ty)


class Formula(ABC):
    description: Dict[str, Tuple[str, type]]

    @abstractmethod
    def to_node(self) -> Equal:
        pass

    def explain(self):
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
            max_type_length = len(format_type(max(self.description.values(), key=lambda i: len(format_type(i[1])))[1]))
            symbols = []
            for symbol in self.description:
                data = self.description[symbol]
                padded_symbol = symbol + ' ' * (max_symbol_length - len(symbol))
                padded_type = format_type(data[1]) + ' ' * (max_type_length - len(format_type(data[1])))
                message = f"{padded_symbol}: [{padded_type}] {data[0]}"
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

    def solvewhere(self, symbols: Dict[str, Any] = None, **kwargs: Any) -> float:
        solver = Solver(self.to_node())
        return solver.solvewhere(symbols, **kwargs)


if __name__ == '__main__':
    pass
