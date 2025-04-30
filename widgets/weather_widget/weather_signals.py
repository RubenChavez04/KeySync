from PyQt6.QtCore import QObject, pyqtSignal

class WeatherSignals(QObject):
    update_current = pyqtSignal(dict)
    update_hourly = pyqtSignal(dict)
    update_daily = pyqtSignal(dict)

weather_signals = WeatherSignals()