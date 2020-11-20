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
