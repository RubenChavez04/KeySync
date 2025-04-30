import json

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QStackedWidget

from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.weather_widget.current_weather_widget import CurrentWeatherWidget
from widgets.weather_widget.hourly_weather_widget import HourlyWeatherWidget
from widgets.weather_widget.weather_signals import weather_signals
from widgets.weather_widget.weather_tasker import WeatherThreads
from widgets.widget_asset_functions import selected_button


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

        #Tasker stuff
        self.weather_tasker = WeatherThreads.get_instance()
        self.weather_tasker.run_in_thread()
        self.weather_tasker.start()
        self.weather_client = self.weather_tasker.weather_client

        #Create and add widgets
        self.current_widget = CurrentWeatherWidget(self, self.width, self.height, self.weather_client)
        self.addWidget(self.current_widget)
        self.hourly_widget = HourlyWeatherWidget(self, self.width, self.height)
        self.addWidget(self.hourly_widget)

        global_signal_dispatcher.selected_button.connect(lambda btn: selected_button(self, btn))
        weather_signals.update_current.connect(self.recolor_widget)
        global_signal_dispatcher.delete_button_signal.connect(self.delete_widget)

    def recolor_widget(self, data):
        is_day = data.get("is_day")
        day_night = "day" if is_day == 1 else "night"
        weather_code = data.get("current_weather_code")
        if weather_code != self.weather_code_temp or is_day != self.is_day_temp:
            self.weather_code_temp = weather_code
            self.is_day_temp = is_day
            with open("widgets/weather_widget/weather_codes.json", "r") as f:
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




    def delete_widget(self):
        if self.button_selected==self:
            self.deleteLater()
            global_signal_dispatcher.remove_widget_signal.emit(self)

    def mouseDoubleClickEvent(self,event):
        """Handle double-click to rename the tab."""
        if event.button() == Qt.MouseButton.LeftButton: #if left click twice
            self.button_selected = self
            global_signal_dispatcher.selected_button.emit(self)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """mouse event handling for initializing dragging the widget."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = self.pos() #get mouse position
            self.last_valid_position = self.pos()#save old position for invalid widget placement
        if event.button() == Qt.MouseButton.RightButton:
            if self.currentIndex() == 0:
                self.setCurrentIndex(1)
            else:
                self.setCurrentIndex(0)

    def mouseMoveEvent(self, event: QMouseEvent):
        """mouse event handling for dragging the widget."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            new_pos = self.mapToParent(event.pos()) #calculate mouse position based on initial mouse position
            self.move(self.parent.get_snapped_position(new_pos, self.size_multiplier)) #get a snapped position relative to the mouse pos
            self.parent.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """mouse event handling for releasing the widget and saving its pos if valid"""
        if event.button() == Qt.MouseButton.LeftButton:
            #get the snapped position for widget
            snapped_pos = self.parent.get_snapped_position(self.pos(), self.size_multiplier)
            #temporarily remove old positions, so widget can be moved 1 col over if needed
            self.parent.remove_widget_position(self)

            #check if the snapped position is valid to prevent overlapping
            if self.parent.is_position_available(snapped_pos, self.size_multiplier): #if the position in grid is valid
                self.move(snapped_pos)  #move the widget to the snapped position
                self.parent.save_widget_position(self, snapped_pos)  #save the new position
                self.last_valid_position = snapped_pos  #update last valid position
            else: #if position is invalid revert to old position from press event
                self.parent.save_widget_position(self, self.last_valid_position)  #restore old position
                self.move(self.last_valid_position)  #revert to old position
        self.parent.update()

