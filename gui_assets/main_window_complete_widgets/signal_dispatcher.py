from PyQt6.QtCore import QObject, pyqtSignal, QPoint
from PyQt6.QtWidgets import QPushButton



class SignalDispatcher(QObject):
    add_widget_signal = pyqtSignal()
    selected_button = pyqtSignal(QPushButton)
    update_position = pyqtSignal(QPushButton)

# Create a global dispatcher instance
global_signal_dispatcher = SignalDispatcher()
