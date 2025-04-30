from datetime import datetime
import json

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from widgets.weather_widget.weather_signals import weather_signals
from widgets.widget_asset_functions import create_drop_shadow


class HourlyWeatherWidget(QWidget):
    def __init__(self, parent, size_x, size_y):
        super().__init__(parent)
        self.setFixedSize(size_x,size_y)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.hour_labels = []
        self.weather_codes_temp = []
        self.is_day_temp = []
        start_x = 10
        start_y = 10
        spacing_x = 65
        spacing_y =100

        for i in range(6):
            hour_label = HourLabel(self)
            if i>2:
                hour_label.move(start_x +((i-3)*spacing_x), start_y + spacing_y)
            else:
                hour_label.move(start_x +(i*spacing_x), start_y)
            hour_label.setGraphicsEffect(create_drop_shadow())
            self.hour_labels.append(hour_label)

        weather_signals.update_current.connect(self.update_hourly_values)

    def update_hourly_values(self, data):
        hourly_temp = data.get("hourly_temp")
        hours = data.get("hours")
        weather_codes = data.get("hourly_weather_codes")
        now = datetime.now()
        current_hour = now.strftime("%I%p")
        current_hour = current_hour.lstrip("0") #remove leading zero for comparison
        current_hour = "12PM"
        current_index = hours.index(current_hour)
        next_hours = hours[current_index:current_index+6]
        next_temps = hourly_temp[current_index:current_index+6]
        next_weather_codes = weather_codes[current_index:current_index+6]

        for i, hour_label in enumerate(self.hour_labels):
            if i < len(next_temps):
                hour_label.set_hour_temp(next_hours[i], f"{next_temps[i]}°")
                hour_label.set_icon(next_weather_codes[i],1)

class HourLabel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        #hour label
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hour_label = QLabel(self)
        self.hour_label.setText("00AM")
        self.hour_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 18px;
                color: white;
            }
        """)
        self.hour_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hour_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.layout.addWidget(self.hour_label)

        #weather_icon
        self.weather_icon = QLabel("", self)
        self.weather_icon.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.weather_icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.weather_icon.setFixedSize(35,35)
        self.layout.addWidget(self.weather_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        #temp_label
        self.temperature_label = QLabel("000°",self)
        self.temperature_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 18px;
                color: white;
        }""")
        self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temperature_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.layout.addWidget(self.temperature_label)
        self.set_icon(1,1)

    def set_hour_temp(self,hour,temp):
        self.hour_label.setText(hour)
        self.temperature_label.setText(temp)
        self.hour_label.update()
        self.temperature_label.update()

    def set_icon(self,weather_code, is_day):
        day_night = "day" if is_day == 1 else "night"
        with open("widgets/weather_widget/weather_codes.json", "r") as f:
            weather_data = json.load(f)
        weather_code_str = str(weather_code)
        if weather_code_str in weather_data:
            current_weather_code_data = weather_data[weather_code_str][day_night]
        else:
            return
        # get weather icon and set the image
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

