import json
import os

import requests
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QTransform, QColor
from PyQt6.QtWidgets import QWidget, QLabel, QSlider, QPushButton, QGraphicsDropShadowEffect

from pi_code.signal_dispatcher_pi import pi_signal_dispatcher
from widgets.widget_asset_functions import create_rounded_icon


class ClientSpotifyWidget(QPushButton):
    def __init__(self, parent, cell_size, size_multiplier=(4, 2), position=None, color="#f0f0f0"):
        #needed a size multiplier for determining col and row span [0] is col [1] is row
        super().__init__(parent)
        #variables
        self.button_selected = None
        self.is_playing_temp = None
        self.parent = parent
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier

        self.setFixedSize(cell_size * size_multiplier[0] + (size_multiplier[0]*13)-13, #width = 100 * (how much columns to take) + spacing
                              cell_size * size_multiplier[1] + (size_multiplier[1]*20)-20)
        self.width = cell_size * size_multiplier[0] + (size_multiplier[0]*13)-13
        self.height = cell_size * size_multiplier[1] + (size_multiplier[1]*20)-20
        self.startPos = None
        self.last_valid_position = position if position else QPoint(0, 0)
        self.move(self.last_valid_position)

        #set saved color on restore or use default if new
        self.color = color
        self.setStyleSheet(
            f"QPushButton {{border-radius: 8px;background-color: {self.color};border: None;}} QPushButton:hover {{ background-color: #cccccc;}}")

        # Add album art label
        self.album_art_label = QLabel(self)
        self.album_art_label.setFixedSize(163, 163)
        self.album_art_label.move(7, 7)
        self.album_art_label.setStyleSheet("""
            QLabel { 
                background-color: transparent;
                border: none;
            }
        """)

        # Add track name label
        self.track_name_label = QLabel("No Track Playing", self)
        self.track_name_label.setFixedSize(250, 25)
        self.track_name_label.move(180, 5)
        self.track_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.track_name_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 21px;
                color: white;
            }
        """)
        track_shadow = create_drop_shadow()
        self.track_name_label.setGraphicsEffect(track_shadow)
        # Add artist name label

        self.artist_name_label = QLabel("", self)
        self.artist_name_label.setFixedSize(250, 20)
        self.artist_name_label.move(180, 30)
        self.artist_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.artist_name_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: white;
            }
        """)
        artist_shadow = create_drop_shadow()
        self.artist_name_label.setGraphicsEffect(artist_shadow)
        track_shadow = create_drop_shadow()
        self.track_name_label.setGraphicsEffect(track_shadow)
        self.track_name_label.setAutoFillBackground(False)
        self.artist_name_label.setAutoFillBackground(True)

        #Define playback control parameters
        playback_fixed_size = int(40)
        playback_x = 285
        playback_y = 120
        playback_spacing_x = int(50*1.7)
        playback_spacing_y = int(-50 * 1.2)
        # Add play/pause button

        self.playback_button = self.create_playback_button(
            "client_assets/play_icon.png",
            (lambda: pi_signal_dispatcher.send_func_signal.emit("spotify:playback")),
            playback_fixed_size,
            (playback_x, playback_y)
        )
        # Add previous button
        self.previous_button = self.create_playback_button(
            "client_assets/skip_icon.png",
            (lambda: pi_signal_dispatcher.send_func_signal.emit("spotify:previous")),
            playback_fixed_size,
            (playback_x-playback_spacing_x, playback_y),
            True
        )

        # Add skip button
        self.next_button = self.create_playback_button(
            "client_assets/skip_icon.png",
            (lambda: pi_signal_dispatcher.send_func_signal.emit("spotify:skip")),
            playback_fixed_size,
            (playback_x+playback_spacing_x, playback_y)
        )

        #Add shuffle button
        self.shuffle_button = self.create_playback_button(
            "client_assets/shuffle_icon.png",
            (lambda: pi_signal_dispatcher.send_func_signal.emit("spotify:shuffle")),
            playback_fixed_size,
            (playback_x - int(playback_spacing_x / 2), playback_y + playback_spacing_y)
            )

        # Add repeat button
        self.repeat_button = self.create_playback_button(
            "client_assets/repeat_icon.png",
            (lambda: pi_signal_dispatcher.send_func_signal.emit("spotify:repeat")),
            playback_fixed_size,
            (playback_x + int(playback_spacing_x / 2), playback_y + playback_spacing_y)
        )

        # Add playback slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.progress_slider.setFixedSize(439 - 100, 10)
        self.progress_slider.setStyleSheet("""
                                        QSlider::groove:horizontal {
                                            border: 1px solid #000000;
                                            height: 8px;
                                            background: #000000;
                                            border-radius: 4px;
                                        }
                                        QSlider::handle:horizontal {
                                            background: #ffffff;
                                            border: 1px solid #ffffff;
                                            width: 14px;
                                            height: 14px;
                                            margin: -3px 0;
                                            border-radius: 7px;
                                        }
                                        QSlider::sub-page:horizontal {
                                            background: #ffffff;
                                            border-radius: 4px;
                                        }
                                    """)
        self.progress_slider.move(50, 220 - 30)  #Below the playback button

        self.label_stylesheet = """
                            QLabel {
                                background-color: #f0f0f0;
                                border: none;
                                font-weight: bold;
                                color: black;
                            }
                        """
        #Add progress label
        self.progress_label = QLabel("0:00", self)
        self.progress_label.setFixedSize(50, 20)
        self.progress_label.move(15, 183)  # Position to the left of the slider
        self.progress_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-weight: bold;
                color: white;
            }
        """)
        progress_shadow = create_drop_shadow()
        self.progress_label.setGraphicsEffect(progress_shadow)
        self.progress_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        #Add duration label
        self.duration_label = QLabel("0:00", self)
        self.duration_label.setFixedSize(50, 20)
        self.duration_label.move(390, 183)  #Position to the right of the slider
        self.duration_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-weight: bold;
                color: white;
            }
        """)
        duration_shadow = create_drop_shadow()
        self.duration_label.setGraphicsEffect(duration_shadow)
        self.duration_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.update_widget()
        pi_signal_dispatcher.update_spotify_widget.connect(self.update_widget)
        pi_signal_dispatcher.update_spotify_progress.connect(self.update_slider)

    def update_slider(self, incoming):
        result = incoming.split(':')
        progress = int(result[1])
        is_playing = result[2]
        if is_playing != self.is_playing_temp:
            self.is_playing_temp = is_playing
            if is_playing == 'True':
                self.playback_button.setIcon(QIcon("client_assets/pause_icon.png"))
            else:
                self.playback_button.setIcon(QIcon("client_assets/play_icon.png"))
        self.progress_slider.setValue(progress)
        self.progress_label.setText(f"{progress // 60000}:{(progress // 1000) % 60:02}")

    def update_widget(self):
        if not os.path.exists("client_assets/spotify_data.json"):
            print("spotify_data.json not found")
            return
        try:
            with open("client_assets/spotify_data.json") as file:
                data = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading spotify data: {e}")
            return
        image_url = data.get("url")
        palette = data.get("palette")
        name = data.get("name")
        artist = data.get("artist")
        duration = data.get("duration")

        if image_url:
            # Update the album art image
            response = requests.get(image_url, timeout=5)
            image_data = response.content
            image = QPixmap()
            image.loadFromData(image_data)
            rounded_pixmap = create_rounded_icon(image, self.album_art_label.size(), radius=5)
            self.album_art_label.setPixmap(rounded_pixmap)
        if palette:
            try:
                # Extract the main two colors from the palette
                color1 = "#{:02x}{:02x}{:02x}".format(*palette[0])
                color2 = "#{:02x}{:02x}{:02x}".format(*palette[1])

                # Update the background gradient with the extracted colors
                self.setStyleSheet(f"""
                       QPushButton {{
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
                print(f"Failed to apply ColorThief colors: {str(e)}")
        if name:
            self.track_name_label.setText(name)
        if artist:
            self.artist_name_label.setText(artist)
        if duration:
            self.progress_slider.setMaximum(duration)
            self.duration_label.setText(f"{duration // 60000}:{(duration // 1000) % 60:02}")
        self.update()

    def create_playback_button(self, icon_path, click_callback, size, position, rotate = False):
        button = QPushButton(self)
        button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        button.setFixedSize(size,size)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        button.move(*position)
        button.setGraphicsEffect(
            create_drop_shadow()
        )
        button.setIconSize(button.size())
        button.clicked.connect(click_callback)
        if rotate:
            pixmap = QPixmap(icon_path)
            transform = QTransform().rotate(180)
            rotated_pixmap = pixmap.transformed(transform)
            rotated_icon = QIcon(rotated_pixmap)
            button.setIcon(rotated_icon)
        else:
            button.setIcon(QIcon(icon_path))

        return button

def create_drop_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(13)
    shadow.setOffset(1, 1)
    shadow.setColor(QColor(0, 0, 0, 200))
    return shadow