import json
from PyQt6.QtCore import QObject, QThread, QTimer, QThreadPool

from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.weather_widget.open_meteo_client import OpenMeteoClient
from widgets.weather_widget.weather_tasks import GetWeatherInfo


class WeatherThreads(QObject):
    _instance = None

    @staticmethod #does not require self and allows the widgets to get the same instance
    def get_instance():
        if WeatherThreads._instance is None:
            # instance of WeatherThreads all weather_widgets use
            WeatherThreads._instance = WeatherThreads()
        return WeatherThreads._instance

    def __init__(self,update_interval = 60000):
        super().__init__()
        if WeatherThreads._instance is not None:
            raise Exception("Only one weather widget allowed")

        self.weather_client = OpenMeteoClient()
        self.update_interval = update_interval
        self.timer = QTimer()
        self.thread_pool = QThreadPool()
        self.worker_thread = None

        self.timer.timeout.connect(self.run_tasks)
        self.run_tasks()

    def run_in_thread(self):
        if self.worker_thread:
            print("Weather threads already running")
            return
        self.worker_thread = QThread()
        self.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.start)
        self.worker_thread.finished.connect(self.cleanup)
        self.worker_thread.start()

    def start(self):
        print("Starting WeatherThread timer")
        self.timer.start(self.update_interval)

    def stop(self):
        print("Stopping WeatherThread timer")
        self.timer.stop()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

    def cleanup(self):
        print("Cleaning up WeatherThreads thread")

    def run_tasks(self):
        get_weather_info_task = GetWeatherInfo(self.weather_client)
        self.thread_pool.start(get_weather_info_task)