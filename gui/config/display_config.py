import os
from typing import Optional, List, Any, Callable

from cli.cli_parser import CLIParser
from cli.helpable import Helpable


class DisplayHelper(Helpable):
    def help_for(self, key: str) -> str:
        try:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'helps', key + '.help')
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "cannot find help message"

    def contains_key(self, key) -> bool:
        return key in DisplayConfig.config_keys

    def help(self) -> str:
        message = []
        for key in DisplayConfig.config_keys:
            message.append(f'[{key}]' + ":\n" + self.help_for(key))

        return '\n'.join(message)


class DisplayConfig:
    config_keys = ['cdir', 'spath', 'lvl']
    config: Optional[dict]
    parser: CLIParser

    def __init__(self, parser: CLIParser):
        parser.parse()
        self.parser = parser

    def value(self, key: str) -> Optional[Any]:
        assert key in DisplayConfig.config_keys
        flag, exist = self.parser.contains(key)
        if not exist:
            return None
        return flag.value

    def value_or_default(self, key: str, default: Callable):
        assert key in DisplayConfig.config_keys
        flag, exist = self.parser.contains(key)
        if not exist:
            return default()
        return flag.value

    def imports(self) -> List[str]:
        return self.parser.imports()