from PyQt6.QtCore import QObject, pyqtSignal


class SignalDispatcher(QObject):
    add_widget_signal = pyqtSignal()


# Create a global dispatcher instance
global_signal_dispatcher = SignalDispatcher()
