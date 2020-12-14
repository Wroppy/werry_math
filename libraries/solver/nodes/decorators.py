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