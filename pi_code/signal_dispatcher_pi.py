from PyQt6.QtCore import QObject, pyqtSignal

class SignalDispatcher(QObject):
    change_page_signal = pyqtSignal(int)
    send_func_signal = pyqtSignal(str)


pi_signal_dispatcher = SignalDispatcher()
