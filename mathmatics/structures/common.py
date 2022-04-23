from abc import abstractmethod, ABC

from mathmatics.webserver.desmos import start_desmos


class MathObject(ABC):
    @abstractmethod
    def to_latex(self) -> str:
        pass

    def open_in_desmos(self):
        """
        Open this object by opening it in Desmos

        :return:
        """
        latex = self.to_latex()
        if latex is None:
            start_desmos()
        else:
            start_desmos(latex)


class Range:
    def __init__(self, start:float, end:float, step: float = 1):
        self.start = start
        self.end = end
        self.step = step

    def __str__(self):
        return f"[start={self.start}, end={self.end}, step={self.step}]"

    def __repr__(self):
        return f"Range(start={self.start}, end={self.end}, step={self.step})"


    def __iter__(self):
        yield self.start
        yield self.end
        yield self.step