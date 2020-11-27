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
    return pH * pEH / (pH * pEH + (1-pH) * pnEH)


if __name__ == '__main__':
    print(bayes_theorem(1/21, 0.4, 0.1))