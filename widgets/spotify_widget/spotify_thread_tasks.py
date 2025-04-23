import io
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, QTimer
from PyQt6.QtWidgets import QMessageBox
from colorthief import ColorThief
from widgets.spotify_widget.spotify import SpotifyIntegration
from widgets.spotify_widget.spotify_signals import spotify_signals

class GetTrackInfoTask(QRunnable):
    def __init__(self, spotify, whats_playing):
        super().__init__()
        self.sp = spotify
        self.wp = whats_playing

    def run(self):
        try:
            if self.sp.sp:
                current_track = self.sp.get_current_playing()
                if current_track:
                    if current_track["name"] != self.wp:
                        url = current_track.get("album_art_url")
                        name = current_track["name"]
                        artist = current_track["artist"]
                        duration = current_track["duration_ms"]
                        response = requests.get(url, timeout=5)
                        image_data = response.content
                        # Use ColorThief to extract the main color palette
                        color_thief = ColorThief(io.BytesIO(image_data))
                        palette = color_thief.get_palette(color_count=2, quality=1)

                        # Ensure the palette has at least two colors
                        if len(palette) < 2:
                            palette.append(palette[0])  # Duplicate the first color if there is only one

                        # Emit both image data and color palette
                        spotify_signals.album_art_update.emit({
                            "image_data": image_data,
                            "palette": palette,
                            "name": name,
                            "artist": artist,
                            "duration": duration
                        })

        except Exception as e:
            print(f"Failed to fetch album info or extract palette: {str(e)}")
            # Emit an empty result in case of failure
            spotify_signals.album_art_update.emit({
                "image_data": None,
                "palette": None,
                "name": None,
                "artist": None
            })

class UpdateSliderTask(QRunnable):
    def __init__(self, spotify_client):
        super().__init__()
        self.spotify_client = spotify_client

    def run(self):
        # Perform the Spotify API call in the background
        try:
            current_track = self.spotify_client.get_current_playing()
            if current_track:
                # Pack the slider progress and track duration
                progress = current_track["progress_ms"]
                playback = self.spotify_client.sp.current_playback()
                is_playing = playback["is_playing"]

                spotify_signals.slider_update.emit({
                    "progress": progress,
                    "is_playing": is_playing
                })
            else:
                # Emit default values if no track is playing
                spotify_signals.slider_update.emit({"progress": 0, "duration": 1})
        except Exception as e:
            print(f"Error in update_slider task: {e}")
            spotify_signals.slider_update.emit({"progress": 0, "duration": 1})  # Emit default values on failure

