import win32con
from PySide6 import QtWidgets, QtGui, QtCore

import hotkey
from pkg import logs
from ui_py.ui_ragdoll import Ui_MainWindow
from . import screen_window


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    activate_sig = QtCore.Signal()

    def __init__(self, parent=None, hk_manager: hotkey.HotkeyManager = None):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        if hk_manager is not None:
            hk_manager.register(
                hotkey.Hotkey(
                    self.activate_sig.emit,
                    hotkey.HotkeyFsModifiers.MOD_NONE,
                    win32con.VK_F4,
                )
            )

        self.fullscreen_widget: screen_window.ScreenWindow | None = None
        self.screenshot_btn.clicked.connect(self.screenshot)
        self.activate_sig.connect(self.screenshot)

    def screenshot(self):
        if self.fullscreen_widget is not None and self.fullscreen_widget.isVisible():
            return

        screen = QtGui.QGuiApplication.primaryScreen()
        if self.screen() is not None:
            screen = self.screen()

        if screen is None:
            logs.error("screen is None")
            return

        self.fullscreen_widget = screen_window.ScreenWindow()
        original_pixmap = screen.grabWindow(0)
        self.fullscreen_widget.display(original_pixmap)
