from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout
import random
import os

from pi_code.pi_widgets.button_widget_pi import ClientButtonWidget  # Ensure the adjusted ButtonWidget is imported here.
from pi_code.pi_widgets.spotify_widget.spotify_widget_pi import ClientSpotifyWidget
from pi_code.pi_widgets.weather_widget.weather_widget_pi import WeatherWidget


class Page(QWidget):
    def __init__(self, parent, image_path=None):
        super().__init__(parent)

        self.image_path = image_path

        # Main page layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Frame for the page content
        self.frame = QFrame(self)
        self.frame.setFixedSize(800, 480)  # Set to Pi screen size (fixed dimensions)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Frame layout
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        # Add page grid into the frame
        self.page_grid = PageGrid(self)
        frame_layout.addWidget(self.page_grid)

        # Add frame to the main layout
        layout.addWidget(self.frame)
        self.setLayout(layout)

        # Set the background
        self.set_background(self.image_path)

    def set_background(self, image_path):
        if image_path and os.path.exists(image_path):
            # File exists, use it
            self.frame.setStyleSheet(f"""
                QFrame {{
                    background-image: url({image_path});
                    background-repeat: no-repeat;
                    background-position: center;
                    background-size: cover;
                    border-radius: 0px;
                }}
            """)
        else:
            self.frame.setStyleSheet("""
                QFrame 
                    background: black;
                    border-radius: 0px;
            """)
        self.update()


class PageGrid(QWidget):
    grid_full = pyqtSignal(bool)

    def __init__(self, frame):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Transparent background
        self.setContentsMargins(0, 0, 0, 0)

        self.frame = frame
        self.rows = 4
        self.cols = 7
        self.cell_size = 100
        self.vertical_spacing = 20
        self.horizontal_spacing = 13
        self.top_bottom_margins = 10
        self.left_right_margins = 11

        self.setFixedSize(800, 480)

        self.widgets = []
        self.positions = {}

    def add_widget(self, widget_type, size_multiplier=(1, 1), position=None, color="#f0f0f0", label="",
                   image_path=None):
        if position is None:
            position = self.find_first_available_position(size_multiplier)
        if not position or not isinstance(position, QPoint):
            print(f"Invalid widget position: {position}. Skipping.")
            return
        if not isinstance(size_multiplier, tuple) or len(size_multiplier) != 2:
            print(f"Invalid size_multiplier: {size_multiplier}. Skipping.")
            return

        if widget_type in ["ButtonWidget", "1x1 button", "2x2 button"]:
            try:
                widget = ClientButtonWidget(self, self.cell_size, size_multiplier, position, color, label, image_path)
            except Exception as e:
                print(f"Error occurred while adding widget: {e}")
                return
        elif widget_type == "WeatherWidget":
            try:
                widget = WeatherWidget(self, self.cell_size, size_multiplier, position)
            except Exception as e:
                print(f"Error occurred while adding widget: {e}")
                return
        elif widget_type == "SpotifyWidget":
            try:
                widget = ClientSpotifyWidget(self,self.cell_size, size_multiplier, position, color)
            except Exception as e:
                print(f"Error occurred while adding widget: {e}")
                return
        else:
            print(f"Unknown widget type: {widget_type}. Skipping.")
            return
        #move and display the widget
        widget.move(position)
        self.widgets.append(widget)
        self.save_widget_position(widget, position)
        widget.show()


    def save_widget_position(self, widget, pos):
        size_multiplier = widget.size_multiplier  # Dimensions of the widget
        for row_offset in range(size_multiplier[1]):
            for col_offset in range(size_multiplier[0]):
                #calculate each cell's position
                cell_x = pos.x() + col_offset * (self.cell_size + self.horizontal_spacing)
                cell_y = pos.y() + row_offset * (self.cell_size + self.vertical_spacing)
                #skip if out of grid bounds
                if cell_x < self.left_right_margins or cell_y < self.top_bottom_margins or \
                        cell_x >= (self.cols * (self.cell_size + self.horizontal_spacing)) or \
                        cell_y >= (self.rows * (self.cell_size + self.vertical_spacing)):
                    continue
                #mark the cell as occupied
                self.positions[(cell_x, cell_y)] = widget

    def find_first_available_position(self, size_multiplier=(1, 1)):
        for row in range(self.rows - size_multiplier[1] + 1):
            for col in range(self.cols - size_multiplier[0] + 1):
                #calculate the top-left position for the widget
                pos = QPoint(
                    self.left_right_margins + col * (self.cell_size + self.horizontal_spacing),
                    self.top_bottom_margins + row * (self.cell_size + self.vertical_spacing),
                )
                #check if the position is valid
                if self.is_position_available(pos, size_multiplier):
                    return pos
        return None

    def is_position_available(self, pos, size_multiplier=(1, 1)):
        for row_offset in range(size_multiplier[1]):
            for col_offset in range(size_multiplier[0]):
                #calculate the position of each cell within the widget’s size
                cell_x = pos.x() + col_offset * (self.cell_size + self.horizontal_spacing)
                cell_y = pos.y() + row_offset * (self.cell_size + self.vertical_spacing)

                if cell_x < self.left_right_margins or \
                        cell_y < self.top_bottom_margins or \
                        cell_x >= (self.cols * (self.cell_size + self.horizontal_spacing)) or \
                        cell_y >= (self.rows * (self.cell_size + self.vertical_spacing)):
                    return False

                # Check whether the cell is already occupied
                if (cell_x, cell_y) in self.positions:
                    return False
        return True
