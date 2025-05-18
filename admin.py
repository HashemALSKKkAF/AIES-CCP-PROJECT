from PyQt6.QtWidgets import QMainWindow
from gui.main_window import MainWindow

class Admin(QMainWindow):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Admin, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True

        # Your init code here
        self.main_window = MainWindow()
        self.setCentralWidget(self.main_window)
        self.setWindowTitle("Multimodal Translator App")
        self.resize(800, 600)
