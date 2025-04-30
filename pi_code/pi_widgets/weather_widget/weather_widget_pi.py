import json
import os.path

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QStackedWidget

from gui_assets.signal_dispatcher import global_signal_dispatcher
from pi_code.pi_widgets.weather_widget.current_weather_widget_pi import CurrentWeatherWidget
from pi_code.pi_widgets.weather_widget.hourly_weather_widget_pi import HourlyWeatherWidget
from pi_code.signal_dispatcher_pi import pi_signal_dispatcher


class WeatherWidget(QStackedWidget):
    def __init__(self, parent, cell_size, size_multiplier=(2, 2), position=None):
        super().__init__(parent)

        self.button_selected = None
        self.is_day_temp = None
        self.weather_code_temp = None
        self.parent = parent
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier
        self.startPos = None  # move widget var

        self.setStyleSheet("""
            QStackedWidget {
                border-radius: 8px;
                border: none;
                background: qlineargradient(
                    spread:pad,
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffe7a3,
                    stop: 1 #1994ff
                );
            }
        """)

        # Size calculation
        self.width = cell_size * size_multiplier[0] + (size_multiplier[0] * 13) - 13
        self.height = cell_size * size_multiplier[1] + (size_multiplier[1] * 20) - 20
        self.setFixedSize(self.width, self.height)

        self.last_valid_position = position if position else QPoint(0, 0)
        self.move(self.last_valid_position)

        # Create and add widgets
        self.current_widget = CurrentWeatherWidget(self, self.width, self.height)
        self.addWidget(self.current_widget)
        self.hourly_widget = HourlyWeatherWidget(self, self.width, self.height)
        self.addWidget(self.hourly_widget)
        pi_signal_dispatcher.update_weather_widget.connect(self.recolor_widget)

    def recolor_widget(self):
        if os.path.exists("client_assets/weather_data.json"):
            try:
                with open("client_assets/weather_data.json", "r") as file:
                    data = json.load(file)
                is_day = data.get("is_day")
                day_night = "day" if is_day == 1 else "night"
                weather_code = data.get("current_weather_code")
                if weather_code != self.weather_code_temp or is_day != self.is_day_temp:
                    self.weather_code_temp = weather_code
                    self.is_day_temp = is_day
                    with open("pi_widgets/weather_widget/weather_codes.json", "r") as f:
                        weather_data = json.load(f)
                    weather_code_str = str(weather_code)
                    if weather_code_str in weather_data:
                        current_weather_code_data = weather_data[weather_code_str][day_night]
                    else:
                        return
                    colors = current_weather_code_data["colors"]
                    colors_length = len(colors)
                    if colors_length == 3:
                        color1 = colors[0]
                        color2 = colors[1]
                        color3 = colors[2]
                        self.setStyleSheet(f"""
                            QStackedWidget {{
                                border-radius: 8px;
                                border: none;
                                background: qlineargradient(
                                    spread:pad,
                                    x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 {color1},
                                    stop: 0.5 {color2},
                                    stop: 1 {color3}
                                );
                            }}
                        """)

                    else:
                        color1 = colors[0]
                        color2 = colors[1]
                        self.setStyleSheet(f"""
                            QStackedWidget {{
                                border-radius: 8px;
                                border: none;
                                background: qlineargradient(
                                    spread:pad,
                                    x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 {color1},
                                    stop: 1 {color2}
                                );
                            }}
                        """)
            except Exception as e:
                print(f"Error occurred recoloring weather widget: {e}")

    def delete_widget(self):
        if self.button_selected == self:
            self.deleteLater()
            global_signal_dispatcher.remove_widget_signal.emit(self)

    def mousePressEvent(self, event: QMouseEvent):
        """mouse event handling for initializing dragging the widget."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = self.pos()  # get mouse position
            self.last_valid_position = self.pos()  # save old position for invalid widget placement
        if event.button() == Qt.MouseButton.RightButton:
            if self.currentIndex() == 0:
                self.setCurrentIndex(1)
            else:
                self.setCurrentIndex(0)


