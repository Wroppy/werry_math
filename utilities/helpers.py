# this file is for repl helper functions, may make this run on start #
def describe(func):
    print(f"""{'-'*20}
description for {func.__name__}
doc: {func.__doc__}
params types: {func.__annotations__}
{'-'*20}""")


def test_modules():
    print("testing installation of gui")
    from mathmatics.statistics.theorem import central_limit_theorem
    central_limit_theorem(50, 30, 10000)
    input("enter to continue: ")

    from mathmatics.geometry.equation import QuadraticEquation
    QuadraticEquation(1, 2, 3).graph()
    input("enter to continue: ")

    QuadraticEquation(2, 3, 4).open_in_desmos()
    input("enter to continue: ")

    from chemistry.kinetics.gas import RealGasLaw
    RealGasLaw().to_latex()
    RealGasLaw().open_latex()
    input("enter to continue: ")

    from physics import Halflife
    Halflife().explain()
    print(Halflife().solvewhere({
        "t": 521,
        "N": 312312,
        "N_{0}": 123
    }))
    input("enter to continue: ")

    from mathmatics.abstract.chaos import LogisticMap
    LogisticMap(3.1, 0.2).graph_r()
    input("enter to exit: ")


if __name__ == '__main__':
    describe(describe)