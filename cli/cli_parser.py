from typing import Union, List, Tuple, Optional

from cli.helpable import Helpable


class EmptyFlagException(Exception):
    """
    Exception thrown when a flag have empty content
    """
    pass


class CLIParserFlag:
    """
    A Command-line flag for the parser
    """
    key: str
    value: Union[str, None]

    def __init__(self, key: str, value: str = None):
        if len(key) == 0 or (value is not None and len(value) == 0):
            raise EmptyFlagException("key or value cannot be empty")

        self.key = key
        self.value = value

    def has_value(self) -> bool:
        """
        If the flag have a value
        :return: If it have a value
        """
        return self.value is not None

    def to_module_str(self) -> str:
        """
        Returns the key or value as a module
        :return: Module
        """
        if self.value is None:
            return self.key
        return self.value

    def to_import_str(self) -> str:
        """
        Returns the flag as a import module statement
        :return: A import statement
        """
        if self.value is None:
            return f"from {self.key} import *"
        return f"import {self.key} as {self.value}"

    def __str__(self) -> str:
        if self.value is None:
            return f"{self.key}"
        return f"{self.key} as {self.value}"


class CLIParser:
    """
    Command-line parser implementation\n
    Parses commands in format of\n
    key=value or key
    """
    args: List[str]
    flags: List[CLIParserFlag]
    helpable: Optional[Helpable]
    separator = '='

    def __init__(self, args: List[str], helpable: Helpable = None):
        self.args = args
        self.flags = []
        self.helpable = helpable

    def parse(self) -> List[CLIParserFlag]:
        """
        Parses its arguments
        :return: A list of parser flags
        """

        if len(self.flags) > 0:
            return self.flags

        self.flags = []
        for arg in self.args:
            if CLIParser.separator in arg:
                k, v = arg.split(CLIParser.separator)
                self.add_flag(CLIParserFlag(k, v))
            else:
                self.add_flag(CLIParserFlag(arg))

        if self.helpable is not None:
            if self.contains(self.helpable.help_key)[1]:
                message = []
                for flag in self.flags:
                    if flag.key == self.helpable.help_key:
                        continue
                    message.append(f'[{flag.key}]' + ':\n' + self.helpable.help_for(flag.key))
                print('displaying help message')
                if len(message) == 0:
                    print(self.helpable.help())
                else:
                    print('\n'.join(message))
                quit(0)
        return self.flags

    def add_flag(self, flag: CLIParserFlag):
        self.flags.append(flag)

    def contains(self, key: str) -> Tuple[Optional[CLIParserFlag], bool]:
        """
        If the parses contains a flag with key
        :param key: The key to search for
        :return: (Flag|None, Success)
        """
        for flag in self.flags:
            if flag.key == key:
                return flag, True

        return None, False

    def empty(self) -> bool:
        """
        Is the parser empty
        :return: Is empty
        """
        return len(self.args) == 0

    def is_ignored(self, key: str) -> bool:
        if self.helpable is None:
            return False
        return self.helpable.contains_key(key)

    def modules(self) -> List[str]:
        """
        Gets the list of modules
        :return: The parser flags as module strings
        """
        modules = []
        for flag in self.flags:
            if self.is_ignored(flag.key):
                continue
            modules.append(flag.to_module_str())
        return modules

    def imports(self) -> List[str]:
        imports = []
        for flag in self.flags:
            if self.is_ignored(flag.key):
                continue
            imports.append(flag.to_import_str())
        return imports
