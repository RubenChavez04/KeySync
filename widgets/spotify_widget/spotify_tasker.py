from PyQt6.QtCore import QObject, QThread, QTimer, QThreadPool
from widgets.spotify_widget.spotify import SpotifyIntegration
from widgets.spotify_widget.spotify_signals import spotify_signals
from widgets.spotify_widget.spotify_thread_tasks import GetTrackInfoTask, UpdateSliderTask


class SpotifyThreads(QObject):
    _instance = None  # Singleton instance

    @staticmethod
    def get_instance():
        # Ensure there is a single instance of the SpotifyThreads tasker
        if SpotifyThreads._instance is None:
            SpotifyThreads._instance = SpotifyThreads()
        return SpotifyThreads._instance

    def __init__(self, update_interval=1000):
        super().__init__()
        if SpotifyThreads._instance is not None:
            raise Exception("Only one SpotifyThreads instance allowed!")

        self.spotify = SpotifyIntegration(
            client_id="bc32cd5b33a8461db27327ed3ac05db4",
            client_secret="bf49813610eb4b1ab5648468a157d948",
            redirect_uri="http://localhost:2266/callback"
        )
        self.update_interval = update_interval
        self.timer = QTimer()  # Timer for periodic updates
        self.thread_pool = QThreadPool()  # To manage background threads
        self.worker_thread = None  # Thread to run this tasker
        self.whats_playing = None

        # Authenticate Spotify Integration
        if not self.spotify.sp:
            print("Spotify client not authenticated. Attempting to authenticate...")
            try:
                self.spotify.authenticate()
                print("Authentication successful")
            except Exception as e:
                print(f"Authentication failed: {str(e)}")
        else:
            current_track = self.spotify.get_current_playing()
            print(current_track.get('progress_ms', 'No progress'))

        # Connect the timer to the periodic update task
        self.timer.timeout.connect(self.run_tasks)
        spotify_signals.album_art_update.connect(self.get_whats_playing)

    def run_in_thread(self):
        """Run SpotifyThreads on its own thread."""
        if self.worker_thread:
            print("SpotifyThreads is already running in its own thread.")
            return

        # Create and setup a dedicated thread
        self.worker_thread = QThread()
        self.moveToThread(self.worker_thread)

        # Start the thread and begin task execution
        self.worker_thread.started.connect(self.start)  # Start the timer when thread starts
        self.worker_thread.finished.connect(self.cleanup)  # Cleanup resources when thread stops
        self.worker_thread.start()
        print("running in thread")

    def start(self):
        """Start the periodic updates."""
        print("Starting SpotifyThreads timer...")
        self.timer.start(self.update_interval)

    def stop(self):
        """Stop the periodic updates and terminate the thread."""
        print("Stopping SpotifyThreads timer...")
        self.timer.stop()

        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()  # Wait for the thread to finish
            self.worker_thread = None  # Reset the thread reference

    def cleanup(self):
        """Clean up after the thread finishes."""
        print("Cleaning up SpotifyThreads thread...")

    def run_tasks(self):
        """Run tasks to fetch track info and update playback slider."""
        # Task to update track information
        track_info_task = GetTrackInfoTask(self.spotify, self.whats_playing)
        self.thread_pool.start(track_info_task)

        # Task to update playback slider
        slider_task = UpdateSliderTask(self.spotify)
        self.thread_pool.start(slider_task)

    def get_whats_playing(self, data):
        self.whats_playing = data.get("name")