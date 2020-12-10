from abc import abstractmethod
from typing import Tuple

from common.solver.nodes import *
from common.solver.common import *


class Plugin(ABC):
    @abstractmethod
    def match(self, symbol_side: Node) -> bool:
        pass

    @abstractmethod
    def balance(self, symbol: str, symbol_side: Node, other_side: Node) -> Tuple[Node, Node]:
        pass


class BasicPlugin(Plugin):

    def match(self, symbol_side: Node) -> bool:
        return isinstance(symbol_side, BasicOperations)

    def balance(self, symbol: str, symbol_side: Node, other_side: Node) -> Tuple[Node, Node]:
        operation: BasicOperations = symbol_side
        symbol_side = LEFT_SIDE if operation.left.contain_symbol(symbol) else RIGHT_SIDE

        new_symbol_side = None
        new_other_side = None
        # balancing
        if isinstance(operation, Multiplication):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Division(other_side, operation.right)
            else:
                new_symbol_side = operation.right
                new_other_side = Division(other_side, operation.left)
        elif isinstance(operation, Division):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Multiplication(other_side, operation.right)
            else:
                new_symbol_side = operation.right
                new_other_side = Division(operation.left, other_side)
        elif isinstance(operation, Addition):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Subtraction(other_side, operation.right)
            else:
                new_symbol_side = operation.right
                new_other_side = Subtraction(other_side, operation.left)
        elif isinstance(operation, Subtraction):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Addition(other_side, operation.right)
            else:
                new_symbol_side = operation.right
                new_other_side = Subtraction(operation.left, other_side)

        return new_symbol_side, new_other_side


class AdvancePlugin(Plugin):
    def match(self, symbol_side: Node) -> bool:
        return isinstance(symbol_side, AdvanceOperations)

    def balance(self, symbol: str, symbol_side: Node, other_side: Node) -> Tuple[Node, Node]:
        operation: AdvanceOperations = symbol_side
        symbol_side = LEFT_SIDE if operation.left.contain_symbol(symbol) else RIGHT_SIDE

        new_symbol_side = None
        new_other_side = None

        if isinstance(operation, Power):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Power(operation.right, other_side)
            else:
                new_symbol_side = operation.right
                new_other_side = Logarithm(operation.left, other_side)
        elif isinstance(operation, Root):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Division(Number(1), Logarithm(operation.right, other_side))
            else:
                new_symbol_side = operation.right
                new_other_side = Power(other_side, operation.left)
        elif isinstance(operation, Logarithm):
            if symbol_side == LEFT_SIDE:
                new_symbol_side = operation.left
                new_other_side = Root(other_side, operation.right)
            else:
                new_symbol_side = operation.right
                new_other_side = Power(operation.left, other_side)

        return new_symbol_side, new_other_side
