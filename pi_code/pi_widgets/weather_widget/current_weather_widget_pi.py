import json
import os.path
import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel
from pi_code.signal_dispatcher_pi import pi_signal_dispatcher
from widgets.widget_asset_functions import create_drop_shadow
from datetime import datetime

class CurrentWeatherWidget(QWidget):
    def __init__(self,parent,size_x,size_y):
        super().__init__(parent)
        self.weather_code_temp = None
        self.is_day_temp = None
        self.setFixedSize(size_x,size_y)
        self.setContentsMargins(0,0,0,0)

        #create weather labels
        self.current_temp_label = self.create_label(
            "000°",
            (15, 5),
            50
        )
        self.weather_description = self.create_label(
            "No Weather Description",
            (10, 120),
            27
        )
        self.high_low_label= self.create_label(
            "H:000° L:000°",
            (10, 155),
        )
        self.hourly_rain_prob_label = self.create_label(
            "000%",
            (10, 180)
        )

        #icon for weather code
        self.weather_icon = QLabel("",self)
        self.weather_icon.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.weather_icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.weather_icon.setFixedSize(70,70)
        self.weather_icon.move(130,5)
        self.weather_icon.setGraphicsEffect(create_drop_shadow())
        pi_signal_dispatcher.update_weather_widget.connect(self.update_current_values)

    def update_current_values(self):
        if os.path.exists("client_assets/weather_data.json"):
            try:
                with open ("client_assets/weather_data.json","r") as file:
                    data = json.load(file)
                #set the daily high/low and wind speed
                daily_high = data.get("daily_high")
                daily_low = data.get("daily_low")
                current_wind_speed = data.get("current_wind_speed")
                is_day = data.get("is_day")
                self.high_low_label.setText(f"H:{daily_high}° L:{daily_low}°")

                #set the rain probability
                current_hour = datetime.now().hour
                hourly_rain_prob = data["hourly_rain_prob"][current_hour]
                self.hourly_rain_prob_label.setText(f"{hourly_rain_prob}%")
                #set the current temp
                current_temp = data.get("current_temp")
                self.current_temp_label.setText(f"{current_temp}°")

                #update the weather icon and widget color(eventually)
                current_weather_code = data.get("current_weather_code")
                #only update the icon and description if needed since we are using requests
                if current_weather_code != self.weather_code_temp or is_day != self.is_day_temp:
                    self.is_day_temp = is_day
                    self.weather_code_temp = current_weather_code
                    self.update_weather_icon(current_weather_code, is_day)
            except Exception as e:
                print(f"Error occurred updating current: {e}")

    def create_label(self, text, pos, font_size=21):
        label = QLabel(text, self)
        label.move(*pos)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: {font_size}px;
                color: white;
        }}""")
        label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        label.setGraphicsEffect(create_drop_shadow())
        return label

    def update_weather_icon(self, weather_code, is_day):
        day_night = "day" if is_day == 1 else "night"
        with open("pi_widgets/weather_widget/weather_codes.json", "r") as f:
            weather_data = json.load(f)
        weather_code_str = str(weather_code)
        if weather_code_str in weather_data:
            current_weather_code_data = weather_data[weather_code_str][day_night]
        else:
            return
        #get weather icon and set the image
        weather_icon_url = current_weather_code_data["image"]
        response = requests.get(weather_icon_url, timeout=5)
        weather_icon_data = response.content
        weather_icon = QPixmap()
        weather_icon.loadFromData(weather_icon_data)
        weather_icon = weather_icon.scaled(
            self.weather_icon.width(),
            self.weather_icon.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.weather_icon.setPixmap(weather_icon)

        weather_description = current_weather_code_data["description"]
        self.weather_description.setText(f"{weather_description}")


