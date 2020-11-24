import sys

from mathmatics import *


def eval_loop():
    print("Starting")
    while True:
        try:
            text = input(f"> ")
            try:
                print(eval(text))
            except SystemExit:
                raise KeyboardInterrupt
            except:
                e = sys.exc_info()[1]
                print(str(e))
        except:
            print("Exiting")
            break


if __name__ == '__main__':
    eval_loop()
