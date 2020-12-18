from typing import List

from libraries.solver.common import add_brackets
from libraries.solver.nodes import Decorator, Node, String


# TODO: Add a solver for this
class Sub(Decorator):
    def __init__(self, node: Node, anno: String):
        super().__init__(node)
        self.anno = anno

    def eval(self) -> float:
        return self.node.eval()

    def to_latex(self) -> str:
        return rf"{add_brackets(self.node.to_latex())}_{add_brackets(self.anno.to_latex())}"


class Map(Decorator):
    def __init__(self, node: Node, parameters: List[Node]):
        super(Map, self).__init__(node)
        self.parameters = parameters

    def eval(self) -> float:
        return self.node.eval()

    def to_latex(self) -> str:
        return f"{self.node.to_latex()}({[f'{param.to_latex()} ' for param in self.parameters]})"