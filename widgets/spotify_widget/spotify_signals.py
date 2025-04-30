from PyQt6.QtCore import QObject, pyqtSignal

class SpotifySignals(QObject):
    slider_update = pyqtSignal(dict)
    widget_update = pyqtSignal(dict)

spotify_signals = SpotifySignals()

