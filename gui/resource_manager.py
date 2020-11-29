import os
from typing import Union, Optional

from PyQt5.QtGui import QFont, QFontDatabase, QIcon


class ResourceManager:
    root = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        raise Exception("Cannot create ResourceManger class, this is a singleton")

    @staticmethod
    def get_resource_path(path: str) -> str:
        return os.path.join(ResourceManager.root, "resources", path)

    @staticmethod
    def get_resource_url(path: str) -> str:
        return "/".join(os.path.join(ResourceManager.root, "resources", os.path.sep.join(path.split('/'))).split(os.path.sep))

    @staticmethod
    def load_font(path: str) -> Optional[QFont]:
        _id = QFontDatabase.addApplicationFont(ResourceManager.get_resource_path(os.path.join("fonts", os.path.sep.join(path.split('/')))))
        if _id == -1:
            print(f"Unable to load font '{path}'")
            return None
        fontstr = QFontDatabase.applicationFontFamilies(_id)[0]
        return QFont(fontstr, 0)

    @staticmethod
    def load_icon(path: str) -> QIcon:
        return QIcon(ResourceManager.get_resource_path(path))

if __name__ == '__main__':
    print(ResourceManager.get_resource_path("consolas.ttf"))