import requests
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QMouseEvent, QIcon, QPixmap, QTransform, QColor
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout, QPushButton, QInputDialog, QProgressBar, QSlider, \
    QLabel, QMessageBox, QGraphicsDropShadowEffect

from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.spotify_widget.spotify import SpotifyIntegration

class SpotifyWidget(QPushButton):
    def __init__(self, parent, cell_size, size_multiplier=(1, 1), position=None, color="#f0f0f0"):
        #needed a size multiplier for determining col and row span [0] is col [1] is row
        super().__init__(parent)
        self.button_selected = None
        #define parent grid
        self.parent = parent
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier
        if size_multiplier == (1,1):
            self.setFixedSize(cell_size, cell_size)
        else:
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
        print("Initializing spotify widget")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress_slider)
        self.spotify = SpotifyIntegration(
            client_id="bc32cd5b33a8461db27327ed3ac05db4",
            client_secret="bf49813610eb4b1ab5648468a157d948",
            redirect_uri="http://localhost:2266/callback"
        )
        self.setToolTip("Link Spotify Account")

        if not self.spotify.sp:
            print("Spotify client not authenticated. Attempting to authenticate...")
            try:
                self.spotify.authenticate()
                print("Authentication successful")
            except Exception as e:
                print(f"Authentication failed: {str(e)}")
                QMessageBox.critical(self, "Spotify Error", f"Authentication failed: {str(e)}")
        else:
            current_track = self.spotify.get_current_playing()
            print(current_track['progress_ms'])

        # Add playback visual button
        self.playback_button = QPushButton(self)
        self.playback_button.setFixedSize(40, 40)
        self.playback_button.setStyleSheet("""
                            QPushButton {
                                border-radius: 20px;
                                background-color: #1DB954;
                                border: 2px solid #1DB954;
                                padding-left: 5px;
                            }
                            QPushButton:hover {
                                background-color: #1ED760;
                            }
                        """)
        self.playback_button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.playback_button.setToolTip("Playback Control")
        self.playback_button.move(199, 140)
        print("playback before icon")
        play_icon = QIcon("gui_assets/gui_icons/play_icon.png")
        self.playback_button.setIcon(play_icon)
        self.playback_button.setIconSize(self.playback_button.size() / 2)
        self.playback_button.clicked.connect(self.toggle_playback)


        # Add album art label
        self.album_art_label = QLabel(self)
        self.album_art_label.setFixedSize(100, 100)
        self.album_art_label.move(
            (self.album_art_label.width() - self.album_art_label.width()) // 2,
            self.album_art_label.height()  - 225
        )
        self.album_art_label.setStyleSheet("""
                            QLabel { 
                                background-color: transparent;
                                border: none;
                            }
                        """)
        print("album art added")
        # Add track name label
        self.track_name_label = QLabel("No Track Playing",self)
        self.track_name_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.track_name_label.setFixedSize(439 - 20, 20)
        self.track_name_label.move(10, 220 - 130)  # Position above the playback button
        self.track_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_name_label.setStyleSheet("""
                            QLabel {
                                background-color: #000000;
                                border: none;
                                font-weight: bold;
                                font-size: 14px;
                                color: black;
                            }
                        """)
        print("Track name added")
        # Add artist name label
        self.artist_name_label = QLabel("",self)
        self.artist_name_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.artist_name_label.setFixedSize(439 - 20, 20)
        self.artist_name_label.move(10, 110)  # Position below the song name
        self.artist_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_name_label.setStyleSheet("""
                            QLabel {
                                background-color: #f0f0f0;
                                border: none;
                                font-size: 12px;
                                color: black;
                            }
                        """)
        self.track_name_label.setAutoFillBackground(False)
        self.artist_name_label.setAutoFillBackground(True)

        # Add previous song button
        self.previous_button = QPushButton(self)
        self.previous_button.setFixedSize(30, 30)
        self.previous_button.setStyleSheet("""
                            QPushButton {
                                border-radius: 15px;
                                background-color: #1DB954;
                                border: 2px solid #1DB954;
                                padding-right: 2px;
                            }
                            QPushButton:hover {
                                background-color: #1ED760;
                            }
                        """)
        self.previous_button.setToolTip("Previous Song")
        self.previous_button.move(
            (439 - 40) // 2 - 40,  # Position to the left of playback button
            145
        )
        pixmap = QPixmap("gui_assets/gui_icons/skip_icon.png")
        print("Pixmap made for skip")
        transform = QTransform().rotate(180)
        rotated_pixmap = pixmap.transformed(transform)
        rotated_icon = QIcon(rotated_pixmap)
        self.previous_button.setIcon(rotated_icon)
        self.previous_button.setIconSize(self.previous_button.size() / 2)
        self.previous_button.clicked.connect(self.previous_song)

        print("previous song added")

        #Add next song button
        self.next_button = QPushButton(self)
        self.next_button.setFixedSize(30, 30)
        self.next_button.setStyleSheet("""
                            QPushButton {
                                border-radius: 15px;
                                background-color: #1DB954;
                                border: 2px solid #1DB954;
                                padding-left: 4px; 
                            }
                            QPushButton:hover {
                                background-color: #1ED760;
                            }
                        """)
        self.next_button.setToolTip("Next Song")
        self.next_button.move(
            (439 - 40) // 2 + 50,  #Put to the right of playback button
            220 - 75
        )
        skip_icon = QIcon("gui_assets/gui_icons/skip_icon.png")
        self.next_button.setIcon(skip_icon)
        self.next_button.setIconSize(self.next_button.size() / 2)
        self.next_button.clicked.connect(self.next_song)
        print("next song added")

        # Add playback slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.progress_slider.setFixedSize(439 - 100, 10)
        self.progress_slider.setStyleSheet("""
                                        QSlider::groove:horizontal {
                                            border: 1px solid #737373;
                                            height: 8px;
                                            background: #e0e0e0;
                                            border-radius: 4px;
                                        }
                                        QSlider::handle:horizontal {
                                            background: #1DB954;
                                            border: 1px solid #1DB954;
                                            width: 14px;
                                            height: 14px;
                                            margin: -3px 0;
                                            border-radius: 7px;
                                        }
                                        QSlider::sub-page:horizontal {
                                            background: #1DB954;
                                            border-radius: 4px;
                                        }
                                    """)
        self.progress_slider.move(50, 220 - 30)  #Below the playback button
        self.progress_slider.sliderReleased.connect(self.set_playback_position)

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
        self.progress_label.move(15, 220 - 35)  # Position to the left of the slider
        self.progress_label.setStyleSheet(self.label_stylesheet)
        self.progress_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        #Add duration label
        self.duration_label = QLabel("0:00", self)
        self.duration_label.setFixedSize(50, 20)
        self.duration_label.move(439 - 40, 220 - 35)  #Position to the right of the slider
        self.duration_label.setStyleSheet(self.label_stylesheet)
        self.duration_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.timer.start(1000)  # Update once a second


    def toggle_playback(self):
        if not self.spotify.sp:
            print("Spotify client not authenticated. Please authenticate first.")
            return
        try:
            self.spotify.play_pause()
            self.update_progress_slider()
        except Exception as e:
            print(f"Playback toggle failed: {str(e)}")
            QMessageBox.critical(self, "Spotify Error", f"Playback toggle failed: {str(e)}")

    def update_progress_slider(self):
        if not self.spotify.sp:
            return
        try:
            current_track = self.spotify.get_current_playing()
            if current_track:
                progress = current_track["progress_ms"]
                duration = current_track["duration_ms"]

                # Update slider
                self.progress_slider.setMaximum(duration)
                self.progress_slider.setValue(progress)

                # Update labels
                self.progress_label.setText(f"{progress // 60000}:{(progress // 1000) % 60:02}")
                self.duration_label.setText(f"{duration // 60000}:{(duration // 1000) % 60:02}")

                # Update track name
                self.track_name_label.setText(current_track["name"])

                self.artist_name_label.setText(current_track["artist"])

                self.album_art_label.setFixedSize(75, 75)  # New size for album art
                self.album_art_label.move(
                    (439 - self.album_art_label.width()) // 2,  # Center horizontally
                    220 - self.playback_button.height() - 170  # Adjust position if needed
                )

                # Update album art
                album_art_url = current_track.get("album_art_url")
                if album_art_url:
                    image = QPixmap()
                    image.loadFromData(requests.get(album_art_url).content)
                    scaled_image = image.scaled(
                        self.album_art_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.album_art_label.setPixmap(scaled_image)
                else:
                    self.album_art_label.clear()
            else:
                self.track_name_label.setText("No Track Playing")
                self.artist_name_label.setText("")
                self.album_art_label.clear()
        except Exception as e:
            print(f"Failed to update progress slider: {str(e)}")

    def set_playback_position(self):
        if not self.spotify.sp:
            return
        try:
            new_position = self.progress_slider.value()
            self.spotify.sp.seek_track(new_position)
        except Exception as e:
            print(f"Failed to set playback position: {str(e)}")

    def previous_song(self):
        if not self.spotify.sp:
            print("Spotify client not authenticated. Please authenticate first.")
            return
        try:
            self.spotify.sp.previous_track()
            print("Skipped to previous track.")
            self.update_progress_slider()
        except Exception as e:
            print(f"Failed to skip to previous track: {str(e)}")

    def next_song(self):
        if not self.spotify.sp:
            print("Spotify client not authenticated. Please authenticate first.")
            return
        try:
            self.spotify.sp.next_track()
            print("Skipped to next track.")
            self.update_progress_slider()
        except Exception as e:
            print(f"Failed to skip to next track: {str(e)}")


    def selected_button(self, button_selected):
        self.button_selected = button_selected

        if self.button_selected == self:
            # Set shadow effect for an external border
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setColor(QColor(0, 255, 42, 255))  # Border/Outline color
            shadow.setBlurRadius(30)  # Remove blur, make a solid border
            shadow.setOffset(0, 0)  # Center the border around the widget
            shadow.setXOffset(0)  # No offset along X-axis
            shadow.setYOffset(0)  # No offset along Y-axis

            self.setGraphicsEffect(shadow)  # Apply the effect
        else:
            # Remove shadow effect when deselected
            self.setGraphicsEffect(None)
        self.update()

    def mouseDoubleClickEvent(self,event):
        """Handle double-click to rename the tab."""
        if event.button() == Qt.MouseButton.LeftButton: #if left click twice
            self.button_selected = self
            global_signal_dispatcher.selected_button.emit(self)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """mouse event handling for initializing dragging the widget."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.pos() #get mouse position
            self.last_valid_position = self.pos()#save old position for invalid widget placement


    def mouseMoveEvent(self, event: QMouseEvent):
        """mouse event handling for dragging the widget."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            new_pos = self.mapToParent(event.pos() - self.startPos) #calculate mouse position based on initial mouse position
            self.move(self.parent.get_snapped_position(new_pos, self.size_multiplier)) #get a snapped position relative to the mouse pos

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