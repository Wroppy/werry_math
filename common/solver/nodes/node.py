from abc import ABC, abstractmethod
from typing import Callable, Optional


class CannotEvalSymbol(Exception):
    def __init__(self, symbol: str):
        super(CannotEvalSymbol, self).__init__(f"cannot evaluate symbol {symbol}")


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

    def contain_symbol(self, symbol: str) -> bool:
        if self.contains_symbol is not None:
            return self.contains_symbol
        has_symbol = self.has_symbol(symbol)
        self.contains_symbol = has_symbol
        return has_symbol

    @abstractmethod
    def has_symbol(self, symbol: str) -> bool:
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

class Operation(Node, ABC):
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
