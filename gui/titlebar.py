from gui.imports import *
from gui.imports.extras import *

import ctypes
from ctypes import wintypes

import win32api
import win32con
import win32gui


class MINMAXINFO(ctypes.Structure):
    _fields_ = [
        ("ptReserved", wintypes.POINT),
        ("ptMaxSize", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("ptMinTrackSize", wintypes.POINT),
        ("ptMaxTrackSize", wintypes.POINT),
    ]


class LabelWithDragSignal(QLabel):
    mousePress = pyqtSignal(QMouseEvent)
    mouseMove = pyqtSignal(QMouseEvent)
    dblClicked = pyqtSignal()

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.mousePress.emit(ev)
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.mouseMove.emit(ev)
        super().mouseMoveEvent(ev)

    def mouseDoubleClickEvent(self, ev: QMouseEvent) -> None:
        self.dblClicked.emit()
        super().mouseDoubleClickEvent(ev)


class ResizeType:
    NONE = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4
    LEFT_TOP = 5
    LEFT_BOTTOM = 6
    RIGHT_TOP = 7
    RIGHT_BOTTOM = 8


class WidgetWithDragSignal(QWidget):
    mousePress = pyqtSignal(QMouseEvent)
    mouseMove = pyqtSignal(QMouseEvent)
    mouseRelease = pyqtSignal(QMouseEvent)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.mousePress.emit(ev)
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.mouseMove.emit(ev)
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.mouseRelease.emit(ev)
        super().mouseReleaseEvent(ev)


class WindowWithTitlebar(QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)

        # constants
        self._borderSize = 4

        # windows stuff
        self._rect = QApplication.instance().desktop().availableGeometry(self)


        # window calls
        self.setWindowFlags(Qt.Window |
                            Qt.FramelessWindowHint
                            | Qt.WindowSystemMenuHint
                            | Qt.WindowMinimizeButtonHint
                            | Qt.WindowMaximizeButtonHint
                            | Qt.WindowCloseButtonHint)

        style = win32gui.GetWindowLong(int(self.winId()), win32con.GWL_STYLE)
        win32gui.SetWindowLong(int(self.winId()), win32con.GWL_STYLE, style | win32con.WS_THICKFRAME)

        if QtWin.isCompositionEnabled():
            # Aero Shadow
            QtWin.extendFrameIntoClientArea(self, -1, -1, -1, -1)
        else:
            QtWin.resetExtendedFrame(self)

        # TODO: fix this so it works with docks
        # main content
        self._central = WidgetWithDragSignal()
        # strecth central
        self._central.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # remove margins
        self.setLayout(QVBoxLayout())

        # expand layout
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._central)

        # set central to window size
        self._central.setFixedSize(self.size())

        self._central.setLayout(QVBoxLayout())
        self._central.layout().setContentsMargins(self._borderSize, self._borderSize, self._borderSize,
                                                         self._borderSize)



        # titlebar
        self._iconLabel = QLabel()
        self._titleLabel = QLabel()
        self._titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._titleLabel.setObjectName("titleLabel")
        self._minimizeBtn = QPushButton("\u23af")
        self._maximizeBtn = QPushButton("\u20de")
        self._closeBtn = QPushButton("\u2715")
        self._minimizeBtn.setCursor(Qt.ArrowCursor)
        self._maximizeBtn.setCursor(Qt.ArrowCursor)
        self._closeBtn.setCursor(Qt.ArrowCursor)

        self._titleWidget = QWidget()
        self._titleWidget.setObjectName("titleWidget")

        self._titleWidget.setLayout(QHBoxLayout())
        self._titleWidget.layout().addWidget(self._iconLabel)
        self._titleWidget.layout().addWidget(self._titleLabel)
        self._titleWidget.layout().addWidget(self._minimizeBtn)
        self._titleWidget.layout().addWidget(self._maximizeBtn)
        self._titleWidget.layout().addWidget(self._closeBtn)
        self._titleWidget.layout().setSpacing(0)
        self._titleWidget.layout().setContentsMargins(0, 0, 0, self._borderSize)
        self._titleWidget.setCursor(Qt.ArrowCursor)

        self._content = QWidget()
        self._content.setLayout(QVBoxLayout())
        self._content.layout().setContentsMargins(0, 0, 0, 0)
        self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._central.layout().addWidget(self._titleWidget)
        self._central.layout().addWidget(self._content)

        # set title dragging
        self._titleLabel.setCursor(Qt.ArrowCursor)

        # set resize window
        self._type = ResizeType.NONE
        self._pressed = False

        self._central.mouseMove.connect(self.handleMove)
        self._central.mousePress.connect(self.handlePress)
        self._central.mouseRelease.connect(self.handleRelease)
        self._central.setMouseTracking(True)

        # titlebar buttons
        self._minimizeBtn.setFixedSize(55, 25)
        self._maximizeBtn.setFixedSize(55, 25)
        self._closeBtn.setFixedSize(55, 25)
        # titlebar buttons event
        self._minimizeBtn.clicked.connect(self.showMinimized)
        self._maximizeBtn.clicked.connect(self.handleMaximize)
        self._closeBtn.clicked.connect(self.close)

        # set titlebar buttons style
        style = """
                  QPushButton {
                      background-color: transparent;
                      border-radius: 0;
                      color: #f2f2f2;
                      font-size: 14px;
                      font-weight: bold;
                      }
                  QPushButton:hover {
                      background-color: #555;
                      color: #f2f2f2;
                      }
              """
        self._minimizeBtn.setStyleSheet(style)
        self._maximizeBtn.setStyleSheet(style)
        self._closeBtn.setStyleSheet(style + """
            QPushButton:hover {
                 background-color: red;
                 color: #f2f2f2;
            }
        """)
        # minimum size
        # self.minimumX = 300
        # self.minimumY = 300
        # self.setMinimumSize(self.minimumX, self.minimumY)

        # set stylesheet
        self.setStyleSheet("""
            QMainWindow {
                # background-color: white;
            }
            QWidget#titleWidget {
                border-bottom: 1px solid #e0e0e0;
            }
        """)

    def resizeEvent(self, event):
        self._central.setFixedSize(self.size())
        super().resizeEvent(event)

    # title events
    def handleMaximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # handles the resize of window
    def handleRelease(self, event: QMouseEvent) -> None:
        self._pressed = False

    def handlePress(self, event: QMouseEvent) -> None:
        self._pressed = True
        self.setResizeType(event)

    def setResizeType(self, event):
        borderSize = self._borderSize

        right = event.pos().x() >= self.width() - borderSize
        bottom = event.pos().y() >= self.height() - borderSize
        left = event.pos().x() <= borderSize
        top = event.pos().y() <= borderSize
        if top and right:
            self._type = ResizeType.RIGHT_TOP
        elif top and left:
            self._type = ResizeType.LEFT_TOP
        elif bottom and right:
            self._type = ResizeType.RIGHT_BOTTOM
        elif bottom and left:
            self._type = ResizeType.LEFT_BOTTOM
        elif right:
            self._type = ResizeType.RIGHT
        elif bottom:
            self._type = ResizeType.BOTTOM
        elif left:
            self._type = ResizeType.LEFT
        elif top:
            self._type = ResizeType.TOP
        else:
            self._type = ResizeType.NONE

        # change cursor
        if self._type == ResizeType.NONE:
            self.setCursor(Qt.ArrowCursor)
        elif self._type == ResizeType.RIGHT:
            self.setCursor(Qt.SizeHorCursor)
        elif self._type == ResizeType.BOTTOM:
            self.setCursor(Qt.SizeVerCursor)
        elif self._type == ResizeType.RIGHT_BOTTOM:
            self.setCursor(Qt.SizeFDiagCursor)
        elif self._type == ResizeType.LEFT_BOTTOM:
            self.setCursor(Qt.SizeBDiagCursor)
        elif self._type == ResizeType.LEFT:
            self.setCursor(Qt.SizeHorCursor)
        elif self._type == ResizeType.TOP:
            self.setCursor(Qt.SizeVerCursor)
        elif self._type == ResizeType.LEFT_TOP:
            self.setCursor(Qt.SizeFDiagCursor)
        elif self._type == ResizeType.RIGHT_TOP:
            self.setCursor(Qt.SizeBDiagCursor)

    def handleMove(self, event: QMouseEvent) -> None:
        if self._pressed:
            # this handles the resizing
            if self._type == ResizeType.NONE:
                return
            if self._type == ResizeType.RIGHT:
                self.resize(event.pos().x(), self.height())
            elif self._type == ResizeType.BOTTOM:
                self.resize(self.width(), event.pos().y())
            elif self._type == ResizeType.RIGHT_BOTTOM:
                self.resize(event.pos().x(), event.pos().y())
            elif self._type == ResizeType.LEFT:
                # this is a bit tricky, we need to resize the window to the right, then move it to the left
                # also stop if the window is too small
                if self.width() - event.pos().x() < self.minimumWidth():
                    return

                self.resize(self.width() - event.pos().x(), self.height())
                self.move(self.pos().x() + event.pos().x(), self.pos().y())
            elif self._type == ResizeType.TOP:
                # this is a bit tricky, we need to resize the window to the bottom, then move it to the top
                # also stop if the window is too small
                if self.height() - event.pos().y() < self.minimumHeight():
                    return

                self.resize(self.width(), self.height() - event.pos().y())
                self.move(self.pos().x(), self.pos().y() + event.pos().y())
            elif self._type == ResizeType.LEFT_TOP:
                # this is a bit tricky, we need to resize the window to the right and bottom, then move it to the left and top
                # also stop if the window is too small
                if self.width() - event.pos().x() < self.minimumWidth() or self.height() - event.pos().y() < self.minimumHeight():
                    return

                self.resize(self.width() - event.pos().x(), self.height() - event.pos().y())
                self.move(self.pos().x() + event.pos().x(), self.pos().y() + event.pos().y())
            elif self._type == ResizeType.RIGHT_TOP:
                # this is a bit tricky, we need to resize the window to the left and bottom, then move it to the right and top
                # also stop if the window is too small
                if event.pos().x() < self.minimumWidth() or self.height() - event.pos().y() < self.minimumHeight():
                    return

                self.resize(event.pos().x(), self.height() - event.pos().y())
                self.move(self.pos().x(), self.pos().y() + event.pos().y())
            elif self._type == ResizeType.LEFT_BOTTOM:
                # this is a bit tricky, we need to resize the window to the right and top, then move it to the left and bottom
                # also stop if the window is too small
                if self.width() - event.pos().x() < self.minimumWidth() or event.pos().y() < self.minimumHeight():
                    return

                self.resize(self.width() - event.pos().x(), event.pos().y())
                self.move(self.pos().x() + event.pos().x(), self.pos().y())

        # keep resizing if pressed
        if self._pressed and self._type != ResizeType.NONE:
            return

        self.setResizeType(event)

    def setWindowTitle(self, title):
        self._titleLabel.setText(title)
        super().setWindowTitle(title)

    def setIcon(self, icon, size=(16, 16)):
        self._iconLabel.setPixmap(icon.pixmap(size[0], size[1]))
        self.setWindowIcon(icon)

    def setCentralWidget(self, widget: QWidget) -> None:
        widget.setCursor(Qt.ArrowCursor)
        super().setCentralWidget(widget)
        self._content.layout().addWidget(widget)

    def nativeEvent(self, eventType, message):
        retval, result = super().nativeEvent(eventType, message)

        # if you use Windows OS
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())

            x = win32api.LOWORD(ctypes.c_long(msg.lParam).value) - self.frameGeometry().x()
            y = win32api.HIWORD(ctypes.c_long(msg.lParam).value) - self.frameGeometry().y()

            if msg.message == win32con.WM_NCCALCSIZE:
                # Remove system title
                return True, 0

            if msg.message == win32con.WM_GETMINMAXINFO:
                # This message is triggered when the window position or size changes.
                info = ctypes.cast(
                    msg.lParam, ctypes.POINTER(MINMAXINFO)).contents
                # Modify the maximized window size to the available size of the main screen.
                info.ptMaxSize.x = self._rect.width()
                info.ptMaxSize.y = self._rect.height()
                # Modify the x and y coordinates of the placement point to (0,0).
                info.ptMaxPosition.x, info.ptMaxPosition.y = 0, 0

            if msg.message == win32con.WM_NCHITTEST:
                # if mouse in on titleLabel
                geometry = self._titleLabel.geometry()
                # make geometry larger to make it easier to click on the title
                geometry.setHeight(geometry.height() + self._borderSize)
                # move geometry down
                geometry.moveTop(geometry.top() + self._borderSize)
                geometry.setWidth(geometry.width() + 10)
                if geometry.contains(x, y):
                    return True, win32con.HTCAPTION

        return retval, result
