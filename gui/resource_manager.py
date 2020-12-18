import os
from typing import Union, Optional, Tuple

from PyQt5.QtGui import QFont, QFontDatabase, QIcon


class ResourceManager:
    """
    This class manages the resources in the gui/resources folder
    """
    root = os.path.dirname(os.path.realpath(__file__))

    default_resource_folder = {
        "font": "fonts",
        "icon": "icons",
        "style": "styles"
    }

    def __init__(self):
        raise Exception("Cannot create ResourceManger class, this is a singleton")

    @staticmethod
    def get_resource_folder(resource: str):
        return ResourceManager.default_resource_folder[resource]

    @staticmethod
    def get_resource_root() -> str:
        return os.path.join(ResourceManager.root, "resources")

    @staticmethod
    def get_resource_location(resource: str, path: str) -> str:
        return os.path.join(ResourceManager.get_resource_root(), ResourceManager.get_resource_folder(resource), path)

    @staticmethod
    def get_resource_url(resource: str, path: str) -> str:
        escaped_path = os.path.sep.join(path.split('/'))
        return "/".join(
            ResourceManager.get_resource_location(resource, escaped_path).split(os.path.sep))

    @staticmethod
    def load_font(path: str) -> Optional[QFont]:
        escaped_path = os.path.sep.join(path.split('/'))
        _id = QFontDatabase.addApplicationFont(ResourceManager.get_resource_location("font", escaped_path))
        if _id == -1:
            print(f"Unable to load font '{path}'")
            return None
        fontstr = QFontDatabase.applicationFontFamilies(_id)[0]
        return QFont(fontstr, 0)

    @staticmethod
    def load_icon(path: str) -> QIcon:
        return QIcon(ResourceManager.get_resource_location("icon", path))

    @staticmethod
    def load_css(path: str) -> str:
        with open(os.path.join(ResourceManager.get_resource_location("style", path)), 'r') as f:
            return f.read()

    @staticmethod
    def join_css(*args) -> str:
        return '\n'.join(args)

    @staticmethod
    def load_css_with_var(path: str, *args: Tuple[str, str]):
        # i don't want to mess with regex so here it is
        css = ResourceManager.load_css(path)
        for old, new in args:
            css = css.replace(old, f"url({new})")
        return css


if __name__ == '__main__':
    print(ResourceManager.get_resource_location("font", "consolas.ttf"))
