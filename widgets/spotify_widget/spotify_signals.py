from PyQt6.QtCore import QObject, pyqtSignal

class SpotifySignals(QObject):
    slider_update = pyqtSignal(dict)
    album_art_update = pyqtSignal(dict)

spotify_signals = SpotifySignals()