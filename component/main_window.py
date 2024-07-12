import win32con
from PySide6 import QtWidgets, QtGui, QtCore

from pkg import logs, hotkey
from ui_py.ui_mainwindow import Ui_MainWindow
from . import clip_window


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    clip_sig = QtCore.Signal()

    def __init__(self, parent=None, hk_manager: hotkey.HotkeyManager = None):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        if hk_manager is not None:
            hk_manager.register(
                hotkey.Hotkey(
                    self.clip_sig.emit,
                    hotkey.HotkeyFsModifiers.MOD_NONE,
                    win32con.VK_F4,
                )
            )

        self.fullscreen_widget: clip_window.ClipWindow | None = None
        self.screenshot_btn.clicked.connect(self.clip)
        self.clip_sig.connect(self.clip)

    def clip(self):
        if self.fullscreen_widget is not None and self.fullscreen_widget.isVisible():
            return

        screen = QtGui.QGuiApplication.primaryScreen()
        if self.screen() is not None:
            screen = self.screen()

        if screen is None:
            logs.error("screen is None")
            return

        original_pixmap = screen.grabWindow(0)
        self.fullscreen_widget = clip_window.ClipWindow(original_pixmap)
