from PyQt6.QtCore import QObject, pyqtSignal

class SignalDispatcher(QObject):
    change_page_signal = pyqtSignal(str)
    send_func_signal = pyqtSignal(str)
    update_spotify_widget = pyqtSignal()
    update_weather_widget = pyqtSignal()
    update_spotify_progress = pyqtSignal(str)
    update_pages = pyqtSignal()

pi_signal_dispatcher = SignalDispatcher()
