def hydrogen_deficiency_index(C: int, H: int, N: int = 0, X: int = 0):
    """
    Returns the hydrogen deficiency index
    A double bond or a ring accounts for one point
    :param C: Number of carbon
    :param H: Number of hydrogen
    :param N: Number of nitrogen
    :param X: Number of halogen
    :return: The hydrogen deficiency index
    """
    return (2 * C + 2 + N - H - X) / 2
