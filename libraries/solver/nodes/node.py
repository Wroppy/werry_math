from abc import ABC, abstractmethod
from typing import Callable, Optional, List, Any, Dict, Union

from utilities.latex import open_latex


class CannotEvalSymbol(Exception):
    def __init__(self, symbol: str):
        super(CannotEvalSymbol, self).__init__(f"cannot evaluate symbol {symbol}")


class CannotEvalString(Exception):
    def __init__(self, string: str):
        super(CannotEvalString, self).__init__(f"cannot evaluate string {string}")


class Node(ABC):
    contains_symbol: Optional[bool]

    def __init__(self):
        self.contains_symbol = None

    @abstractmethod
    def modify(self, mod: Callable):
        pass

    @abstractmethod
    def eval(self) -> float:
        pass

    @abstractmethod
    def has_symbol(self, symbol: str) -> bool:
        pass

    @abstractmethod
    def to_latex(self) -> str:
        pass

    def open_latex(self):
        open_latex(self.to_latex())

    def contain_symbol(self, symbol: str) -> bool:
        if self.contains_symbol is not None:
            return self.contains_symbol
        has_symbol = self.has_symbol(symbol)
        self.contains_symbol = has_symbol
        return has_symbol

    def __add__(self, other) -> 'Symbol':
        raise NotImplementedError
        pass

    def __sub__(self, other) -> 'Symbol':
        raise NotImplementedError
        pass

    def __mul__(self, other) -> 'Symbol':
        raise NotImplementedError
        pass

    def __truediv__(self, other) -> 'Symbol':
        raise NotImplementedError
        pass

    def __pow__(self, power, modulo=None) -> 'Symbol':
        raise NotImplementedError
        pass

    def __eq__(self, other) -> 'Equal':
        raise NotImplementedError
        pass

class StableNode(Node, ABC):
    pass


class Constant(StableNode):
    def __init__(self, symbol: str, value: float):
        super().__init__()
        self.symbol = symbol
        self.value = value

    def modify(self, mod: Callable):
        pass

    def eval(self) -> float:
        return self.value

    def has_symbol(self, symbol: str) -> bool:
        return False

    def to_latex(self) -> str:
        return f"{self.symbol}"


class Symbol(StableNode):
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

    def modify(self, mod: Callable):
        self.symbol = mod(self, self.symbol)

    def eval(self) -> float:
        raise CannotEvalSymbol(self.symbol)

    def has_symbol(self, symbol: str) -> bool:
        if self.symbol == symbol:
            return True
        return False

    def to_latex(self) -> str:
        return f"{self.symbol}"


class Number(StableNode):
    def __init__(self, value: float):
        super().__init__()
        self.value = value
        self.contains_symbol = False

    def modify(self, mod: Callable):
        self.value = mod(self, self.value)

    def eval(self) -> float:
        return self.value

    def has_symbol(self, symbol: str) -> bool:
        return False

    def to_latex(self) -> str:
        return f"{self.value}"


class String(StableNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value
        self.contains_symbol = False

    def modify(self, mod: Callable):
        self.value = mod(self, self.value)

    def eval(self) -> float:
        raise CannotEvalString(self.value)

    def has_symbol(self, symbol: str) -> bool:
        return False

    def to_latex(self) -> str:
        return self.value


class Operation(Node, ABC):
    precedence: int
    left: Node
    right: Node

    def __init__(self, left: Node, right: Node):
        super().__init__()
        self.left = left
        self.right = right

    def modify(self, mod: Callable):
        self.left.modify(mod)
        self.right.modify(mod)
        self.left = mod(self, self.left)
        self.right = mod(self, self.right)

    def has_symbol(self, symbol: str) -> bool:
        return self.left.has_symbol(symbol) or self.right.has_symbol(symbol)

    @staticmethod
    def is_operation(value: Node):
        return isinstance(value, Operation)


class Decorator(Node, ABC):
    node: Node
    ignorable: bool = True

    def __init__(self, node: Node):
        super(Decorator, self).__init__()
        self.node = node

    def to_node(self) -> Node:
        return self.node

    def modify(self, mod: Callable):
        self.node.modify(mod)
        self.node = mod(self, self.node)

    def has_symbol(self, symbol: str) -> bool:
        return self.node.has_symbol(symbol)


class Function(Node, ABC):
    precedence: int = 3
    parameters: List[Node]

    def modify(self, mod: Callable):
        for n in range(len(self.parameters)):
            self.parameters[n].modify(mod)
            self.parameters[n] = mod(self, self.parameters[n])

    def has_symbol(self, symbol: str) -> bool:
        for node in self.parameters:
            if node.has_symbol(symbol):
                return True
        return False

    @staticmethod
    def replace_symbols(symbols: Dict[str, Union[float, int]], function: Node) -> Node:
        def mod(_: Node, value: Any):
            if not isinstance(value, Symbol):
                return value

            if value.symbol in symbols:
                return Number(symbols[value.symbol])
            return value

        function.modify(mod)
        return function


class Equal(Node):
    def __init__(self, left: Node, right: Node):
        super().__init__()
        self.left = left
        self.right = right

    def move(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def modify(self, mod: Callable):
        pass

    def modify_w_callback(self, mod: Callable, callback: Callable):
        self.left.modify(mod)
        self.left = mod(self, self.left)
        callback()
        self.right.modify(mod)
        self.right = mod(self, self.right)

    def eval(self) -> float:
        return 42

    def has_symbol(self, symbol: str) -> bool:
        return True

    def to_latex(self) -> str:
        return f"{self.left.to_latex()}={self.right.to_latex()}"
