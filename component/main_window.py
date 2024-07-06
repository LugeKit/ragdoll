from PySide6 import QtWidgets

from ui_py.ui_ragdoll import Ui_MainWindow


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setupUi(self)
