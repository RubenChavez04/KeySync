import json
from PyQt6.QtCore import QObject, QThread, QTimer, QThreadPool
from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.spotify_widget.spotify import SpotifyIntegration
from widgets.spotify_widget.spotify_signals import spotify_signals
from widgets.spotify_widget.spotify_thread_tasks import GetTrackInfoTask, UpdateSliderTask

#TODO: need to make a signal that can initially update the image when a new widget is added
class SpotifyThreads(QObject):
    _instance = None  #variable to check if an instance is created

    @staticmethod #staticmethod used so an instance of the class can be made within the class
    def get_instance():
        print("spotify_tasker get_instance running")
        #use this method to get instance in spotify widget class
        #check if an instance is created
        if SpotifyThreads._instance is None:
            #create an instance of this class, only gets called when a widget is created
            SpotifyThreads._instance = SpotifyThreads()
            #get currently playing song to save and initialize spotify widgets
            spotify_signals.widget_update.connect(SpotifyThreads._instance.get_whats_playing)

            global_signal_dispatcher.run_spot_func.connect(SpotifyThreads._instance.run_func)
        #if instance has been created, return the already made instance
        return SpotifyThreads._instance

    def __init__(self, update_interval=3000):
        super().__init__()
        if SpotifyThreads._instance is not None:
            raise Exception("Only one SpotifyThreads instance allowed!")

        #create a spotify instance
        self.spotify = SpotifyIntegration(
            client_id="bc32cd5b33a8461db27327ed3ac05db4",
            client_secret="bf49813610eb4b1ab5648468a157d948",
            redirect_uri="http://localhost:2266/callback"
        )

        #variables/objects used
        self.update_interval = update_interval #time in ms for timer to finish and restart
        self.timer = QTimer()  #timer to run tasks
        self.thread_pool = QThreadPool()  #thread pool to sub thread api calls
        self.worker_thread = None  #thread for running the tasker(this) object
        self.whats_playing = None

        #check spotify authentication
        if not self.spotify.sp:
            print("Spotify client not authenticated. Attempting to authenticate...")
            try:
                self.spotify.authenticate()
                print("Authentication successful")
            except Exception as e:
                print(f"Authentication failed: {str(e)}")

        #when timer is done connects to the run_tasks to start thread pool
        #will run function continuously based on the update interval
        self.timer.timeout.connect(self.run_tasks)


    def run_in_thread(self):
        #run this object in its own thread
        if self.worker_thread:
            print("SpotifyThreads is already running in its own thread.")
            return
        #create a worker thread
        self.worker_thread = QThread()
        #move self to worker thread
        self.moveToThread(self.worker_thread)
        #start the instance of objects timer when thread starts
        self.worker_thread.started.connect(self.start)
        #start the worker thread
        self.worker_thread.start()

    def start(self):
        #starts the timer which connects to the run task
        #starts the tasker
        print("starting spotify timer")
        self.timer.start(self.update_interval)

    def stop(self):
        #stop the tasker
        print("stopping spotify timer")
        self.timer.stop()
        #wait for all threads to end and clear threads
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

    def run_tasks(self):
        #create thread_pool tasks to get current track info and progress
        track_info_task = GetTrackInfoTask(self.spotify, self.whats_playing)
        self.thread_pool.start(track_info_task)
        slider_task = UpdateSliderTask(self.spotify)
        self.thread_pool.start(slider_task)

    def get_whats_playing(self, data):
        #get what's currently playing to save resources and only update info
        #if track has changed
        self.whats_playing = data.get("name")
        #save the currently playing data to send to spotify widget on pi
        save_path = "pi_assets/spotify_data.json"
        save_data = {
            "url": data.get("url"),
            "palette": data.get("palette"),
            "name": data.get("name"),
            "artist": data.get("artist"),
            "duration": data.get("duration")
        }
        try:
            with open(save_path,"w") as save_file:
                json.dump(save_data, save_file, indent=4)
            print(f"spotify data saved")
            global_signal_dispatcher.websocket_send_spot.emit()
        except IOError as e:
            print(f"Error occurred saving spotify data: {e}")

    def run_func(self, param):
        if self.spotify:
            if param == "playback":
                self.spotify.play_pause()
            elif param == "previous":
                self.spotify.previous_song()
            elif param == "skip":
                self.spotify.next_song()
            elif param == "shuffle":
                self.spotify.toggle_shuffle()
            elif param == "repeat":
                self.spotify.toggle_repeat()
            else:
                print("Invalid spotify param")
        else:
            print("Spotify not connected")