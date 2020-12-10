from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Callable, Any, Union, Optional

from libraries.solver.nodes import Equal
from libraries.solver.solver import Solver
from utils.latex import open_latex
from utils.markers import Marker


class UnknownSymbol(Exception):
    pass


class ExistingKey(Exception):
    pass


class IncorrectParameterLength(Exception):
    def __init__(self, expected: int, got: int):
        super(IncorrectParameterLength, self).__init__(f"expected {expected}, got {got}")


class IncorrectReturnType(Exception):
    def __init__(self, expected: str, got: str):
        super(IncorrectReturnType, self).__init__(f"expected {expected}, got {got}")


class IncorrectParameterGiven(Exception):
    def __init__(self, position: Union[int, str], expected: str, got: str):
        super(IncorrectParameterGiven, self).__init__(f"at position {position}: expected {expected}, got {got}")


t_parameters = Tuple[Dict[str, type], List[str]]
t_solver = Tuple[Callable, t_parameters, type]


def create_parameters_hint(*args: Tuple[str, type]) -> t_parameters:
    parameters = {}
    types = []

    for arg in args:
        key = arg[0]
        ty = arg[1]
        if key in parameters:
            raise ExistingKey
        parameters[key] = ty
        types.append(key)

    return parameters, types


def create_solver(fn: Callable, details: Optional[Tuple[List[Tuple[str, type]], type]] = None) -> t_solver:
    if details is None:
        annotations = fn.__annotations__
        keys = list(annotations)
        ret_key = keys.pop()
        ret = annotations[ret_key]
        parameters = []
        for key in keys:
            parameters.append((key, annotations[key]))
    else:
        parameters = details[0]
        ret = details[1]
    return fn, create_parameters_hint(*parameters), ret


@Marker.ignore_this
def attempt_cast(data: Any, target: type):
    try:
        return target(data)
    except:
        return None


class Formula(ABC):
    solvers: Dict[str, t_solver] = {}
    symbols: List[str] = []

    def to_latex(self) -> str:
        return self.to_node().to_latex()

    @abstractmethod
    def to_node(self) -> Equal:
        pass

    def open_latex(self):
        latex = self.to_latex()
        if latex is None:
            print("LaTex not available for this equation")
            return
        open_latex(latex)

    def describe(self, unknown: str):
        if unknown not in self.solvers:
            raise UnknownSymbol()

        solver = self.solvers[unknown]

        parameters = solver[1]
        ret_type = solver[2]

        param_text_key = parameters[0]
        param_keys = parameters[1]

        parameters_str = []
        for key in param_keys:
            parameters_str.append(f"{key}: {param_text_key[key]}")

        parameters_str = '\n'.join(parameters_str)
        print(f"""{'-' * 20}
description for solving for {unknown}:
parameters (in order)
{parameters_str}
returns
{ret_type}
{'-' * 20}""")

    def solvewhere(self, symbols: Dict[str, float] = None, **kwargs: Dict[str, float]) -> float:
        solver = Solver(self.to_node())
        return solver.solvewhere(symbols, **kwargs)

    def solvefor(self, unknown: str, *args, **kwargs):
        if unknown not in self.solvers:
            raise UnknownSymbol()

        solver = self.solvers[unknown]

        fn = solver[0]
        parameters = solver[1]
        ret_type = solver.__getitem__(2)

        param_text_type = parameters[0]
        param_keys = parameters[1]

        if len(args) + len(kwargs) != len(param_keys):
            raise IncorrectParameterLength(len(param_keys), len(args) + len(kwargs))

        fn_args = []

        # verify
        for index in range(len(param_keys)):
            param_key = param_keys[index]
            param_type = param_text_type.get(param_key)

            arg = None if index >= len(args) else args[index]
            cast = attempt_cast(arg, param_type)
            if cast is not None:
                fn_args.append(cast)
            elif param_key in kwargs:
                cast = attempt_cast(kwargs[param_key], param_type)
                if cast is None:
                    raise IncorrectParameterGiven(param_key, str(param_type), type(kwargs[param_key]))
                fn_args.append(cast)
            else:
                raise IncorrectParameterGiven(index, str(param_type), type(arg))

        result = fn(*fn_args)

        if not isinstance(result, ret_type):
            raise IncorrectReturnType(str(ret_type), type(result))
        return result


if __name__ == '__main__':
    pass
