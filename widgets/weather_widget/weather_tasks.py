import json
import time

from PyQt6.QtCore import QRunnable

from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.weather_widget.weather_signals import weather_signals


class GetWeatherInfo(QRunnable):
    def __init__(self, weather_client):
        super().__init__()
        self.weather_client = weather_client


    def run(self):
        try:
            time.sleep(2)
            current_weather = self.weather_client.get_current()
            hourly_weather = self.weather_client.get_hourly()
            daily_weather = self.weather_client.get_daily()
            weather_data = {
                "is_day": int(current_weather.get("is_day")),
                
                "daily_high": int(daily_weather["temperature_2m_max"].iloc[0]),
                "daily_low": int(daily_weather["temperature_2m_min"].iloc[0]),
                "daily_rain_prob":int(daily_weather["precipitation_probability_max"].iloc[0]),
                "sunrise": str(daily_weather["sunrise"].iloc[0]),
                "sunset":str(daily_weather["sunset"].iloc[0]),

                "hourly_weather_codes": hourly_weather["weather_codes"].tolist(),
                "hours": hourly_weather["date"].tolist(),
                "hourly_temp":hourly_weather["temperature_2m"].tolist(),
                "hourly_rain_prob":hourly_weather["precipitation_probability"].tolist(),
                "hourly_wind_speed":hourly_weather["wind_speed_10m"].tolist(),

                "current_temp":int(current_weather.get("temperature_2m")),
                "current_weather_code":int(current_weather.get("weather_code")),
                "current_wind_speed":int(current_weather.get("wind_speed_10m"))
            }
            print(int(current_weather.get("weather_code")))
            save_path = "pi_assets/weather_data.json"
            with open(save_path, "w") as f:
                json.dump(weather_data, f, indent=4)
            print("Weather data saved.")

            global_signal_dispatcher.websocket_send_weather.emit()
            weather_signals.update_current.emit(weather_data)
        except Exception as e:
            print(f"Error while updating weather data: {e}")


