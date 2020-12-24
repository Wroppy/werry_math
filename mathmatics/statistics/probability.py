from libraries.solver.nodes import *
from libraries.structures.formula import Formula
from mathmatics.calculus.common import sigma
from mathmatics.statistics.common import choose, ztable
from utilities.graphing import mpl_graph


def bayes_theorem(pH: float, pEH: float, pnEH: float = None) -> float:
    """
    Calculates the bayes theorem for probability that a hypothesis given an evidence

    :param pH: p(Hypothesis)
    :param pEH: p(Evidence given Hypothesis)
    :param pnEH: p(Evidence given ~Hypothesis)
    :return: p(Hypothesis given Evidence)
    """
    if pnEH is None:
        pnEH = 1 - pEH
    return pH * pEH / (pH * pEH + (1 - pH) * pnEH)


def p_and(pA: float, pB: float) -> float:
    return pA * pB


def p_or(pA: float, pB: float, pAandB: float = 0.0) -> float:
    return pA + pB - pAandB


# [ [x1 x2 x3]
#   [p1 p2 p3] ]
def p_mean(data: List[List[float]]) -> float:
    result = 0
    xs = data[0]
    ps = data[1]
    for i in range(len(xs)):
        result += xs[i] * ps[i]

    return result


def p_variance(data: List[List[float]]) -> float:
    _mean = p_mean(data)
    xs = data[0]
    ps = data[1]
    return sigma(
        lambda i: ((xs[i] - _mean) ** 2) * ps[i],
        0,
        len(xs) - 1
    )


def p_standard_deviation(data: List[List[float]]) -> float:
    return math.sqrt(p_variance(data))


class Choose(AdvanceOperations):
    precedence = 3

    def eval(self) -> float:
        total = int(self.left.eval())
        pick = int(self.right.eval())
        return choose(total, pick)

    def to_latex(self) -> str:
        return add_brackets(rf"{self.left.to_latex()} \choose {self.right.to_latex()}")


class BinomialDistribution(Formula):
    """
    Calculates the binomial distribution
    """
    description = {
        "P(n, k)": "The probability of k success in n trials",
        "n": "Number of trials",
        "k": "Number of success required",
        "p": "Probability of success"
    }

    def to_node(self) -> Equal:
        return Symbol("P(n, k)") == Choose(Symbol("n"), Symbol("k")) * Symbol("p") ** Symbol("k") * (
                Number(1) - Symbol("p")) ** (Symbol("n") - Symbol("k"))

    def draw(self, n: int, p: float):
        ks, rs = self.to_data(n, p)

        mpl_graph(ks, rs, type='plot')

    def to_data(self, n: int, p: float) -> Tuple[List[float], List[float]]:
        ks = list(range(0, n + 1))
        rs = []
        for k in ks:
            rs.append(self.solvewhere(n=n, k=k, p=p))
        return ks, rs


class GeometricDistribution(Formula):
    """
    Solves the geometric distributions
    """
    description = {
        'P(k; p)': "Probability for success on the kth trial",
        "k": "Number of trials",
        "p": "Probability of success"
    }

    def to_node(self) -> Equal:
        return Symbol("P(k; p)") == (Number(1) - Symbol("p")) ** (Symbol("k") - Number(1)) * Symbol("p")

    def draw(self, k: int, p: float):
        ks, rs = self.to_data(k, p)
        mpl_graph(ks, rs, type='plot')

    def to_data(self, k: int, p: float) -> Tuple[List[float], List[float]]:
        ks = list(range(1, k + 1))
        rs = []
        for k in ks:
            rs.append(self.solvewhere(k=k, p=p))
        return ks, rs

    def cumulate(self, k: int, p: float):
        return math.fsum(self.to_data(k, p)[1])


def birthday_paradox(people: int) -> float:
    days = 365
    if people >= days:
        return 1

    final = 1
    for i in range(people):
        final *= (days - i) / days
    return 1 - final


def p_value(p: float, s: int, np: float):
    std = (p * (1 - p) / s) ** 0.5
    return ztable((np - p) / std)


def p_value_std():
    pass


if __name__ == '__main__':
    BinomialDistribution().draw(40, 0.2)
    # print(bayes_theorem(1 / 21, 0.4, 0.1))
