import code
import sys
from typing import List, Union

from cli.cli_parser import CLIParser


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
