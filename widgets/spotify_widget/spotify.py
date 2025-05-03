import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from PyQt6.QtWidgets import QInputDialog, QMessageBox
import webbrowser
import timeit

class SpotifyIntegration:
    def __init__(self, client_id, client_secret, redirect_uri, scope=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or "user-read-playback-state user-modify-playback-state user-read-currently-playing"
        self.cache_path = ".cache" #No clue if this is a secure way to do things
        self.sp = None
        self.sp_oauth = None

    def authenticate(self, parent=None):
        # Initialize Spotify OAuth
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path = self.cache_path
        )


        token_info = self.sp_oauth.get_cached_token()
        if token_info:
            self.sp = Spotify(auth=token_info["access_token"])
            #QMessageBox.information(parent, "Spotify", "Spotify account linked successfully!") #Remove this in the future
            return

        auth_url = self.sp_oauth.get_authorize_url()
        print("Opening browser for Spotify authentication")
        webbrowser.open(auth_url)

        response_url, ok = QInputDialog.getText(
            parent,
            "Spotify Authentication",
            "Paste the URL from the opened browser:"
        )

        if not ok or not response_url:
            QMessageBox.warning(parent, "Spotify Error", "Authentication canceled or invalid URL.")
            return

        try:
            code = self.sp_oauth.parse_response_code(response_url)
            token_info = self.sp_oauth.get_access_token(code)

            # Save authcode and initialize Spotify client
            self.sp = Spotify(auth=token_info["access_token"])
            QMessageBox.information(parent, "Spotify", "Spotify account linked successfully!")
        except Exception as e:
            QMessageBox.critical(parent, "Spotify Error", f"Authentication failed: {str(e)}")

    def get_current_playing(self):
        try:
            self.refresh_token()
            if not self.sp:
                print("Spotify is not authenticated. Please authenticate first.")
                return None
            current_track = self.sp.current_user_playing_track()
            if current_track:
                return {
                    "name": current_track["item"]["name"],
                    "artist": ", ".join(artist["name"] for artist in current_track["item"]["artists"]),
                    "album": current_track["item"]["album"]["name"],
                    "progress_ms": current_track["progress_ms"],
                    "duration_ms": current_track["item"]["duration_ms"],
                    "album_art_url": current_track["item"]["album"]["images"][0]["url"],
                }
            return None
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")


    def play_pause(self):
        try:
            self.refresh_token()
            if not self.sp:
                print("Spotify is not authenticated. Please authenticate first.")
                return
            playback = self.sp.current_playback()
            if playback and playback["is_playing"]:
                self.sp.pause_playback()
                print("Playback paused.")
            else:
                self.sp.start_playback()
                print("Playback started.")
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")

    def refresh_token(self):
        try:
            if not self.sp_oauth:
                print("SpotifyOAuth not initialized.")
                return None

            token_info = self.sp_oauth.get_cached_token()

            if not token_info:
                print("No cached token found. Please authenticate again.")
                return None

            if self.sp_oauth.is_token_expired(token_info):
                print("Access token expired. Attempting to refresh...")
                try:
                    token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])

                    # Write updated token to cache (manually)
                    with open(self.cache_path, "w") as f:
                        import json
                        json.dump(token_info, f)

                    self.sp = Spotify(auth=token_info['access_token'])
                    print("Access token refreshed successfully.")
                    return token_info['access_token']
                except Exception as e:
                    print(f"Failed to refresh access token: {e}")
                    return None
            else:
                # Token is still valid
                self.sp = Spotify(auth=token_info['access_token'])
                return token_info['access_token']
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")

    def previous_song(self):
        try:
            if not self.sp:
                print("Spotify client not authenticated. Please authenticate first.")
                return
            try:
                self.sp.previous_track()
                print("Skipped to previous track.")
            except Exception as e:
                print(f"Failed to skip to previous track: {str(e)}")
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")

    def next_song(self):
        try:
            if not self.sp:
                print("Spotify client not authenticated. Please authenticate first.")
                return
            try:
                self.sp.next_track()
            except Exception as e:
                print(f"Failed to skip to next track: {str(e)}")
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")

    def toggle_shuffle(self):
        try:
            if not self.sp:
                return
            try:
                current = self.sp.current_playback()
                if not current:
                    print("No active playback found.")
                    return

                shuffle_state = current["shuffle_state"]
                device_id = current["device"]["id"]

                self.sp.shuffle(not shuffle_state, device_id=device_id)
                print(f"Shuffle {'enabled' if not shuffle_state else 'disabled'} on device {device_id}")
            except Exception as e:
                print(f"Failed to toggle shuffle: {str(e)}")
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")

    def toggle_repeat(self):
        try:
            if not self.sp:
                return
            try:
                current = self.sp.current_playback()
                repeat_state = current["repeat_state"] if current else "off"

                if repeat_state == "off":
                    new_state = "context"
                elif repeat_state == "context":
                    new_state = "track"
                else:
                    new_state = "off"

                self.sp.repeat(new_state)
                print(f"Repeat set to {new_state}")
            except Exception as e:
                print(f"Failed to toggle repeat: {str(e)}")
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")