import time

from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt

from ui_py.ui_ragdoll import Ui_MainWindow
from . import screen_window


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.fullscreen_widget = screen_window.ScreenWindow()
        self.screenshot_btn.clicked.connect(self.screenshot)

    def screenshot(self):
        screen = QtGui.QGuiApplication.primaryScreen()
        if self.screen() is not None:
            screen = self.screen()

        if screen is None:
            print("screen is None")

        original_pixmap = screen.grabWindow(0)
        self.fullscreen_widget.show_fullscreen(original_pixmap)
