# this file is for repl helper functions, may make this run on start #
def describe(func):
    print(f"""{'-'*20}
description for {func.__name__}
doc: {func.__doc__}
params: {func.__code__.co_varnames}
params types: {func.__annotations__}
{'-'*20}""")


if __name__ == '__main__':
    describe(describe)