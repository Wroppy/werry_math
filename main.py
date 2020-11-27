import code
import sys
from typing import List, Union


class EmptyFlagException(Exception):
    pass


class CLIParserFlag:
    key: str
    value: Union[str, None]

    def __init__(self, key: str, value: str = None):
        if len(key) == 0 or (value is not None and len(value) == 0):
            raise EmptyFlagException("key or value cannot be empty")

        self.key = key
        self.value = value

    def to_module_str(self) -> str:
        if self.value is None:
            return self.key
        return self.value

    def to_import_str(self) -> str:
        if self.value is None:
            return f"from {self.key} import *"
        return f"import {self.key} as {self.value}"

    def __str__(self) -> str:
        if self.value is None:
            return f"{self.key}"
        return f"{self.key} as {self.value}"


class CLIParser:
    args: List[str]
    flags: List[CLIParserFlag]
    separator = '='

    def __init__(self, args: List[str]):
        self.args = args
        self.flags = []

    def parse(self) -> List[CLIParserFlag]:
        if len(self.flags) > 0:
            return self.flags

        for arg in self.args:
            if CLIParser.separator in arg:
                k, v = arg.split(CLIParser.separator)
                self.flags.append(CLIParserFlag(k, v))
            else:
                self.flags.append(CLIParserFlag(arg))
        return self.flags

    def empty(self) -> bool:
        return len(self.args) == 0

    def modules(self) -> List[str]:
        modules = []
        for flag in self.flags:
            modules.append(flag.to_module_str())
        return modules


def eval_loop(parser: CLIParser):
    # eval flags
    if parser.empty():
        print("Imported no werry modules")
    else:
        print("Imported werry modules: ")
        for flag in parser.parse():
            exec(flag.to_import_str())
            print(f"    {str(flag)}")

    # define items
    q = quit
    modules = parser.modules()

    # delete parser and start console
    del parser
    code.InteractiveConsole(locals=locals(), filename="<eval_loop>").interact(banner="Type q() to quit", exitmsg="")


if __name__ == '__main__':
    p = CLIParser(sys.argv[1:])
    eval_loop(p)
