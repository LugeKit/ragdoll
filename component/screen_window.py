from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt


class ScreenWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.CustomizeWindowHint)
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel(self)
        self.label.resize(self.screen().size())
        layout.addWidget(self.label, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def mouseDoubleClickEvent(self, event):
        self.close()

    def show_fullscreen(self, img: QtGui.QPixmap | QtGui.QImage):
        self.label.setPixmap(img)
        self.showFullScreen()
