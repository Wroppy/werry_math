import os
from typing import Optional, List, Any, Callable

from cli.cli_parser import CLIParser
from cli.helpable import Helpable
from gui.resource_manager import ResourceManager


class DisplayHelper(Helpable):
    def help_for(self, key: str) -> str:
        try:
            path = ResourceManager.get_resource_location("help", os.path.join(key + '.help'))
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
        self.config = {}

        for key in self.config_keys:
            flag, exist = self.parser.contains(key)
            if exist:
                self.config[key] = flag.value
            else:
                self.config[key] = None

    def value(self, key: str) -> Optional[Any]:
        assert key in self.config_keys
        return self.config[key]

    def value_or_default(self, key: str, default: Callable) -> Any:
        assert key in DisplayConfig.config_keys
        value = self.config[key]
        if value is None:
            self.config[key] = default()
            return self.config[key]
        return value

    def imports(self) -> List[str]:
        return self.parser.imports()
