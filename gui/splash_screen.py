from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QSplashScreen

from gui.common import singleton
from gui.resource_manager import ResourceManager


@singleton
class SplashScreen(QSplashScreen):
    def __init__(self, *args):
        path = ResourceManager.get_resource_url("image", "splash.png")
        size = QSize(400, 225)
        image = QPixmap(path)
        scaled = image.scaled(size, Qt.KeepAspectRatio)
        super().__init__(pixmap=scaled, *args)
        self.font = ResourceManager.load_font("splash/kindamessy.ttf")
        self.font.setPointSize(15)
        self.setFont(self.font)

    def displayMessage(self, message: str):
        super().showMessage(f"{message}...", alignment=Qt.AlignBottom | Qt.AlignRight)
        self.font.setPointSize(15)
        self.setFont(self.font)
