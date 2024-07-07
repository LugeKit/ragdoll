from PySide6 import QtWidgets, QtGui, QtCore

import logs
from ui_py.ui_ragdoll import Ui_MainWindow
from . import screen_window


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    hotkey_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.fullscreen_widget = screen_window.ScreenWindow()
        self.screenshot_btn.clicked.connect(self.screenshot)
        self.hotkey_signal.connect(self.screenshot)

    def screenshot(self):
        if self.fullscreen_widget.isVisible():
            return

        screen = QtGui.QGuiApplication.primaryScreen()
        if self.screen() is not None:
            screen = self.screen()

        if screen is None:
            logs.error("screen is None")

        original_pixmap = screen.grabWindow(0)
        self.fullscreen_widget.display(original_pixmap)
