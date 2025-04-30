from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QMouseEvent
from pycaw.api.endpointvolume import IAudioEndpointVolume
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
import keyboard


from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.spotify_widget.spotify_widget import create_drop_shadow


class MediaWidget(QPushButton):
    def __init__(self, parent, cell_size, size_multiplier=(2, 2), position=None):
        super().__init__(parent)

        self.parent = parent
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier

        self.setFixedSize(cell_size * size_multiplier[0] + (size_multiplier[0] * 13) - 13,
                          # width = 100 * (how much columns to take) + spacing
                          cell_size * size_multiplier[1] + (size_multiplier[1] * 20) - 20)
        self.width = cell_size * size_multiplier[0] + (size_multiplier[0] * 13) - 13
        self.height = cell_size * size_multiplier[1] + (size_multiplier[1] * 20) - 20
        self.startPos = None
        self.last_valid_position = position if position else QPoint(0, 0)
        self.move(self.last_valid_position)

        # set saved color on restore or use default if new
        self.color = "#cfcfcf"
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    spread:pad,
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #A9A9A9,
                    stop: 1 {self.color}
                );
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    spread:pad,
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f0f0,
                    stop: 1 {self.color}
                );
            }}
            QSlider::groove:vertical {{
                width: 8px;
                background: #fff;
                border: none;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                height: 12px;
                background: #A9A9A9;
                border: none;
                border-radius: 3px;
            }}
        """)

        # Create interface for default playback device
        self.audio_device = AudioUtilities.GetSpeakers()
        self.interface = self.audio_device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume_control = self.interface.QueryInterface(IAudioEndpointVolume)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)


        # Playback Button
        self.play_pause_button = QPushButton(self)
        self.play_pause_button.setFixedSize(75, 75)
        self.play_pause_button.setIcon(QIcon("gui_assets/gui_icons/play_icon.png"))
        self.play_pause_button.setIconSize(self.play_pause_button.size()/1.2)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.play_pause_button.move(75, 75)
        self.play_pause_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }
            """)
        self.play_pause_button.setGraphicsEffect(
            create_drop_shadow()
        )

        '''
        # Add play/pause button
        self.playback_button = self.create_playback_button(
            "gui_assets/gui_icons/play_icon.png",
            self.toggle_play_pause(),
            75,
            (75, 75)
        )
        '''
        #Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Vertical, self)
        self.volume_slider.setFixedSize(20, 150)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.get_system_volume())
        self.volume_slider.valueChanged.connect(self.set_system_volume)
        self.volume_slider.move(20, 35)

        self.volume_slider.setGraphicsEffect(
            create_drop_shadow()
        )

        # Add plus button above the volume slider
        self.plus_button = QPushButton("+", self)
        self.plus_button.setFixedSize(20, 20)
        self.plus_button.move(20, 10)  # Position above the slider
        self.plus_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font: bold 26px;
                border-radius: 4px;
            }
        """)
        self.plus_button.setGraphicsEffect(
            create_drop_shadow()
        )
        self.plus_button.clicked.connect(self.increment_volume)

        # Add minus button below the volume slider
        self.minus_button = QPushButton("-", self)
        self.minus_button.setFixedSize(20, 20)
        self.minus_button.move(20, 180)  # Position below the slider
        self.minus_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font: bold 34px;
                border-radius: 4px;
            }
        """)
        self.minus_button.setGraphicsEffect(
            create_drop_shadow()
        )
        self.minus_button.clicked.connect(self.decrement_volume)


        global_signal_dispatcher.delete_button_signal.connect(self.delete_widget)
        #global_signal_dispatcher.selected_button.connect(lambda btn: selected_button(self, btn))


    def toggle_play_pause(self):
        #keyboard signal for pausing and playing media
        keyboard.send("play/pause media")

    def get_system_volume(self):
        return int(self.volume_control.GetMasterVolumeLevelScalar() * 100)

    def set_system_volume(self, value):
        self.volume_control.SetMasterVolumeLevelScalar(value / 100, None)

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

    def mouseMoveEvent(self, event: QMouseEvent):
        """mouse event handling for dragging the widget."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            new_pos = self.mapToParent(event.pos() - self.startPos) #calculate mouse position based on initial mouse position
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

    def increment_volume(self):
        current_volume = self.volume_slider.value()
        if current_volume < 100:  # Ensure volume doesn't exceed 100
            self.volume_slider.setValue(current_volume + 1)

    def decrement_volume(self):
        current_volume = self.volume_slider.value()
        if current_volume > 0:  # Ensure volume doesn't go below 0
            self.volume_slider.setValue(current_volume - 1)

