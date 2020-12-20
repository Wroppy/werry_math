from typing import Union, List, Tuple, Optional


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
    separator = '='

    def __init__(self, args: List[str]):
        self.args = args
        self.flags = []
        self.ignored_modules = []

    def parse(self, ignored_modules=None) -> List[CLIParserFlag]:
        """
        Parses its arguments
        :return: A list of parser flags
        """
        if ignored_modules is None:
            ignored_modules = []

        if len(self.flags) > 0 and ignored_modules == self.ignored_modules:
            return self.flags

        self.flags = []
        self.ignored_modules.extend(ignored_modules)
        for arg in self.args:
            if CLIParser.separator in arg:
                k, v = arg.split(CLIParser.separator)
                self.add_flag(CLIParserFlag(k, v))
            else:
                self.add_flag(CLIParserFlag(arg))
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

    def modules(self) -> List[str]:
        """
        Gets the list of modules
        :return: The parser flags as module strings
        """
        modules = []
        for flag in self.flags:
            if flag.key in self.ignored_modules:
                continue
            modules.append(flag.to_module_str())
        return modules

    def imports(self) -> List[str]:
        imports = []
        for flag in self.flags:
            if flag.key in self.ignored_modules:
                continue
            imports.append(flag.to_import_str())
        return imports
