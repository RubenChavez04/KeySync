import sys
from PyQt6.QtWidgets import QApplication
from gui_assets.main_gui import *
from widgets.functions.getapps import get_apps

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    get_apps()
    sys.exit(app.exec())