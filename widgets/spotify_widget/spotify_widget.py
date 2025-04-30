from PyQt6.QtCore import Qt, QPoint, QThreadPool
from PyQt6.QtGui import QMouseEvent, QIcon, QPixmap, QTransform, QColor
from PyQt6.QtWidgets import QPushButton, QSlider, \
    QLabel, QMessageBox, QGraphicsDropShadowEffect

from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.spotify_widget.spotify_signals import spotify_signals
from widgets.spotify_widget.spotify_tasker import SpotifyThreads
from widgets.widget_asset_functions import create_rounded_icon, selected_button, create_drop_shadow,\
    MarqueeLabel


class SpotifyWidget(QPushButton):
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
        print("Initializing spotify widget")
        #get tasker instance
        self.spotify_tasker = SpotifyThreads.get_instance()  #get the single instance
        self.spotify_tasker.run_in_thread()  #move the instance to run in a thread, if it has not been already
        self.spotify_tasker.start()  #start running the tasks
        self.spotify = self.spotify_tasker.spotify
        print("spotify instance created")
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

        print("spotify works or is not instanced")


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
        self.track_name_label = MarqueeLabel("No track playing", self)
        self.track_name_label.setFixedSize(250, 25)
        self.track_name_label.move(180, 5)
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
            "gui_assets/gui_icons/play_icon.png",
            self.toggle_playback,
            playback_fixed_size,
            (playback_x, playback_y)
        )

        # Add previous button
        self.previous_button = self.create_playback_button(
            "gui_assets/gui_icons/skip_icon.png",
            self.previous_song,
            playback_fixed_size,
            (playback_x-playback_spacing_x, playback_y),
            True
        )

        # Add skip button
        self.next_button = self.create_playback_button(
            "gui_assets/gui_icons/skip_icon.png",
            self.next_song,
            playback_fixed_size,
            (playback_x+playback_spacing_x, playback_y)
        )

        #Add shuffle button
        self.shuffle_button = self.create_playback_button(
            "gui_assets/gui_icons/shuffle_icon.png",
            self.toggle_shuffle,
            playback_fixed_size,
            (playback_x - int(playback_spacing_x / 2), playback_y + playback_spacing_y)
            )

        # Add repeat button
        self.repeat_button = self.create_playback_button(
            "gui_assets/gui_icons/repeat_icon.png",
            self.toggle_repeat,
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

        #self.timer.start(1000)
        #self.update_slider_timer.start(1000)
        self.toggle_playback(init=True)
        global_signal_dispatcher.delete_button_signal.connect(self.delete_widget)
        global_signal_dispatcher.selected_button.connect(lambda btn: selected_button(self,btn))
        spotify_signals.widget_update.connect(self.update_widget)
        spotify_signals.slider_update.connect(self.update_slider)

    def toggle_playback(self,init=False):
        if not self.spotify.sp:
            print("Spotify client not authenticated. Please authenticate first.")
            return
        try:
            if init:
                playback = self.spotify.sp.current_playback()
                if playback and playback["is_playing"]:
                    self.playback_button.setIcon(QIcon("gui_assets/gui_icons/pause_icon.png"))
                else:
                    self.playback_button.setIcon(QIcon("gui_assets/gui_icons/play_icon.png"))
            else:
                self.spotify.play_pause()
                playback = self.spotify.sp.current_playback()
                if playback and playback["is_playing"]:
                    self.playback_button.setIcon(QIcon("gui_assets/gui_icons/pause_icon.png"))
                else:
                    self.playback_button.setIcon(QIcon("gui_assets/gui_icons/play_icon.png"))
        except Exception as e:
            print(f"Playback toggle failed: {str(e)}")
            QMessageBox.critical(self, "Spotify Error", f"Playback toggle failed: {str(e)}")

    def update_slider(self, data):
        #update slider progress and update playback button (if needed)
        progress = data.get("progress", 0)
        is_playing = bool(data.get("is_playing"))
        if is_playing != self.is_playing_temp:
            self.is_playing_temp = is_playing
            if is_playing:
                self.playback_button.setIcon(QIcon("gui_assets/gui_icons/pause_icon.png"))
            else:
                self.playback_button.setIcon(QIcon("gui_assets/gui_icons/play_icon.png"))
        self.progress_slider.setValue(progress)
        self.progress_label.setText(f"{progress // 60000}:{(progress // 1000) % 60:02}")

    def update_widget(self, data):
        #receive data from signal
        image_data = data.get("image_data")
        palette = data.get("palette")
        name = data.get("name")
        artist = data.get("artist")
        duration = data.get("duration")
        if image_data:
            #update
            image = QPixmap()
            image.loadFromData(image_data)
            rounded_pixmap = create_rounded_icon(image, self.album_art_label.size(), radius=5)
            self.album_art_label.setPixmap(rounded_pixmap)
        if palette:
            try:
                #convert rgb values to hex
                color1 = "#{:02x}{:02x}{:02x}".format(*palette[0])
                color2 = "#{:02x}{:02x}{:02x}".format(*palette[1])
                #update the widget background
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
                }}""")
            except Exception as e:
                print(f"Failed to update background: {str(e)}")
        if name:
            self.track_name_label.setText(name) #set song name
        if artist:
            self.artist_name_label.setText(artist) #set artists name(s)
        if duration:
            self.progress_slider.setMaximum(duration) #update the slider duration
            #convert from ms to minutes and seconds to change label
            self.duration_label.setText(f"{duration // 60000}:{(duration // 1000) % 60:02}")

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
        except Exception as e:
            print(f"Failed to skip to previous track: {str(e)}")

    def next_song(self):
        if not self.spotify.sp:
            print("Spotify client not authenticated. Please authenticate first.")
            return
        try:
            self.spotify.sp.next_track()
            print("Skipped to next track.")
        except Exception as e:
            print(f"Failed to skip to next track: {str(e)}")

    def toggle_shuffle(self):
        if not self.spotify.sp:
            return
        try:
            current = self.spotify.sp.current_playback()
            if not current:
                print("No active playback found.")
                return

            shuffle_state = current["shuffle_state"]
            device_id = current["device"]["id"]

            self.spotify.sp.shuffle(not shuffle_state, device_id=device_id)
            print(f"Shuffle {'enabled' if not shuffle_state else 'disabled'} on device {device_id}")
        except Exception as e:
            print(f"Failed to toggle shuffle: {str(e)}")

    def toggle_repeat(self):
        if not self.spotify.sp:
            return
        try:
            current = self.spotify.sp.current_playback()
            repeat_state = current["repeat_state"] if current else "off"

            if repeat_state == "off":
                new_state = "context"
            elif repeat_state == "context":
                new_state = "track"
            else:
                new_state = "off"

            self.spotify.sp.repeat(new_state)
            print(f"Repeat set to {new_state}")
        except Exception as e:
            print(f"Failed to toggle repeat: {str(e)}")

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

