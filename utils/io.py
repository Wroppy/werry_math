import re
from typing import Optional


def prompt_regex(prompt: str, regex: str, default: str = None) -> Optional[str]:
    if default is not None:
        message = f'{prompt}(default is {default}): [{regex}] '
    else:
        message = f'{prompt}: [{regex}] '
    while True:
        try:
            i = input(message)
            if len(i) == 0 and default is not None:
                return default
            if re.fullmatch(regex, i) is not None:
                return i
            else:
                pass
            print("input failed to match, retrying...")
        except Exception as e:
            print(repr(e))
            return None
