from mathmatics.geometry.equation import LinearEquation, QuadraticEquation


def does_it_work():
    print("Yes it does")


if __name__ == '__main__':
    eq = QuadraticEquation(1, 0, -16)
    print(eq.y(1))
    eq.graph()
    print(eq.x_intercepts()[0])