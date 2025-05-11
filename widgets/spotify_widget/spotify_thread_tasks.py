import io
import requests
from PyQt6.QtCore import QRunnable
from colorthief import ColorThief

from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.spotify_widget.spotify_signals import spotify_signals
from server import active_connections


class GetTrackInfoTask(QRunnable):
    def __init__(self, spotify, whats_playing):
        super().__init__()
        self.sp = spotify
        self.wp = whats_playing
    def run(self):
        try:
            if self.sp.sp:
                current_track = self.sp.get_current_playing()
                if current_track: #if a song is playing
                    # check if the currently playing song is still the same
                    if current_track["name"] != self.wp:
                        #get current song information
                        url = current_track.get("album_art_url")
                        name = current_track["name"]
                        artist = current_track["artist"]
                        duration = current_track["duration_ms"]
                        response = requests.get(url, timeout=5)
                        image_data = response.content
                        #use color thief to get image colors, this gets the 2 most dominate colors
                        color_thief = ColorThief(io.BytesIO(image_data))
                        palette = color_thief.get_palette(color_count=2, quality=1)
                        #check the palette's colors is at least 2 if not duplicate the color
                        #needs this because some track art has a single color and will break
                        #the widgets styling
                        if len(palette) < 2:
                            palette.append(palette[0])  #
                        #emit data
                        spotify_signals.widget_update.emit({
                            "image_data": image_data,
                            "url": url,
                            "palette": palette,
                            "name": name,
                            "artist": artist,
                            "duration": duration
                        })

        except Exception as e:
            print(f"Failed to fetch album info or extract palette: {str(e)}")
            # Emit an empty result in case of failure
            spotify_signals.widget_update.emit({
                "image_data": None,
                "palette": None,
                "name": None,
                "artist": None
            })

class UpdateSliderTask(QRunnable):
    def __init__(self, spotify_client):
        super().__init__()
        #retrieve instance of the spotify client from tasker
        self.spotify_client = spotify_client

    def run(self):
        try:
            #get the track playing
            current_track = self.spotify_client.get_current_playing()
            if current_track:
                #get the progress and playback status (playing/paused)
                progress = current_track["progress_ms"]
                playback = self.spotify_client.sp.current_playback()
                is_playing = playback["is_playing"]
                #emit signal to update slider value and playback button
                #playback button update code has a temp value to check before actually updating
                spotify_signals.slider_update.emit({
                    "progress": progress,
                    "is_playing": is_playing
                })
                #if a pi client is connected
                if active_connections:
                    #send the signal to send widget progress
                    global_signal_dispatcher.websocket_send_spot_progress.emit(f"progress:{str(progress)}:{str(is_playing)}")
            else:
                #emit default values if no playback
                spotify_signals.slider_update.emit({"progress": 0, "duration": 1})
        except Exception as e:
            print(f"Error in update_slider task: {e}")
            spotify_signals.slider_update.emit({"progress": 0, "duration": 1})  #emit default values it exception occurs

