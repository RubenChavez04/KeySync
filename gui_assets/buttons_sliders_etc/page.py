import os

from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout

from gui_assets.signal_dispatcher import global_signal_dispatcher
from gui_assets.popups.add_widget_popup import AddWidgetPopup
from widgets.button_widget import ButtonWidget
from widgets.spotify_widget.spotify_widget import SpotifyWidget


class Page(QWidget):
    def __init__(self, parent, image_path="page_backgrounds/wallpaper2.jpg"):

        super().__init__(parent)
        self.index = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.image_path = image_path
        self.frame = QFrame(self)
        self.frame.setFixedSize(800, 480)   #frame size equal to the size of pi screen

        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(frame_layout)
        self.set_background(self.image_path)

        self.page_grid = PageGrid(self)
        frame_layout.addWidget(self.page_grid)

        layout.addWidget(self.frame)

        self.setLayout(layout)
        global_signal_dispatcher.tab_deleted_signal.connect(self.delete_page)

    def show_add_widget_popup(self):
        popup = AddWidgetPopup(self, self.page_grid)
        popup.exec()

    def set_background(self, image_path):
        """set the page background to the given image or default to random gradient."""
        if image_path and os.path.exists(image_path):  # Ensure the file exists
            self.frame.setStyleSheet(f"""
                QFrame {{
                    background-image: url({image_path});
                    background-repeat: no-repeat;
                    background-position: center;
                    background-size: cover;
                    border: 2px solid darkgray;
                }}
            """)
            print("background updated")
        else:
            #default gradient background if no image is set
            self.frame.setStyleSheet(f"""
                QFrame {{
                    background: black;
                    border: 2px solid darkgray;
                }}
            """)
        self.update()

    def update_background(self, image_path):
        """update the background if signal is received"""
        if os.path.exists(image_path):  #ensure the file exists before setting it
            self.image_path = image_path  #store the image path
            self.image_path.replace("\\","/")
            print(f"updated image path - {self.image_path}")
            print("updating background")
            self.set_background(self.image_path)  #apply background change
            print(f"Image file found - {self.image_path}")
        else:
            self.image_path = image_path
            print(f"Error: Image file not found - {self.image_path}")
            self.image_path = None

    def save_page_data(self):
        data = {
            "image_path": self.image_path,
            "widgets":[]
        }

        for widget in self.page_grid.widgets:
            widget_type = widget.__class__.__name__
            if widget_type == "ButtonWidget":
                widget_data = {
                    "type": widget_type,
                    "position": (widget.pos().x(), widget.pos().y()),
                    "size_multiplier": widget.size_multiplier,
                    "color": widget.color,
                    "label": widget.label,
                    "image_path": widget.image_path,
                    "functions": widget.functions
                }
                data["widgets"].append(widget_data)
            elif widget_type == "SpotifyWidget":
                widget_data = {
                    "type": widget_type,
                    "position": (widget.pos().x(), widget.pos().y()),
                    "size_multiplier": widget.size_multiplier
                }
                data["widgets"].append(widget_data)
        return data

    def delete_page(self):
        for widget in self.page_grid.widgets:
            widget.delete_widget()
        self.page_grid.widgets.clear()
        self.page_grid.deleteLater()
        self.deleteLater()


class PageGrid(QWidget):
    """custom grid layout for the frame so we can have a set grid of 4x7 to drag and drop widgets into cells"""
    grid_full = pyqtSignal(bool)
    def __init__(self, frame):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) #make sure the background is transparent, no styling here
        self.setContentsMargins(0,0,0,0)
        self.frame = frame #set frame parent
        self.rows = 4
        self.cols = 7
        self.cell_size = 100            #cell size is 100x100, so each button/widget is this,
                                        #note that each widget will need size adjustments based on the spacings
                                        #all widgets need a size_multiplier to keep track of the rows and columns each take
        self.vertical_spacing = 20      #spacing between rows
        self.horizontal_spacing = 13    #spacing between columns
        self.top_bottom_margins = 10    #margins for the top and bottom of frame
        self.left_right_margins = 11    #margins for the left and right of frame

        self.setFixedSize(800,480)      # set size to frame size

        self.widgets = []   #list of added widgets
        self.positions = {} #dictionary to track widgets

        global_signal_dispatcher.remove_widget_signal.connect(self.remove_widget)

    def add_widget(self, widget_type, size_multiplier=(1, 1), position=None, color="#f0f0f0", label="",image_path= None):
        """Add a widget to the grid, gets called in the pop-up or during restoration."""
        if position is None:
            position = self.find_first_available_position(size_multiplier)
        if not position or not isinstance(position, QPoint):
            print(f"Invalid widget position: {position}. Skipping.")
            return
        if not isinstance(size_multiplier, tuple) or len(size_multiplier) != 2:
            print(f"Invalid size_multiplier: {size_multiplier}. Skipping.")
            return

        available_pos = position if position else self.find_first_available_position(size_multiplier)
        if not available_pos:
            print("No available position for widget. Grid might be full. Skipping.")
            return

        if widget_type == "SpotifyWidget":
            # Example: Add logic specific to Spotify widgets
            widget = SpotifyWidget(self, self.cell_size, size_multiplier, available_pos, color)
        elif widget_type == "1x1 Button" or "2x2 Button" or "ButtonWidget":
            print(color)
            try:
                widget = ButtonWidget(self, self.cell_size, size_multiplier, available_pos, color, label, image_path)
            except Exception as e:
                print(f"Error occurred while adding widget {e}")
                return

            print("widget added")
        else:
            print(f"Unknown widget type: {widget_type}. Skipping.")
            return

        # Proceed with widget placement
        widget.move(available_pos)
        self.widgets.append(widget)
        self.save_widget_position(widget, available_pos)
        widget.show()

        # Check if grid is full
        self.grid_full.emit(self.is_grid_full())

    def save_widget_position(self, widget, pos):
        """save positions for all cells occupied by the widget."""
        size_multiplier = widget.size_multiplier #get the widgets size multiplier
        occupied_cells = []  #list to keep track of all cells in use

        #get cell position
        for row_offset in range(size_multiplier[1]):  #row span
            for col_offset in range(size_multiplier[0]):  #column span
                #get the cells x pos by obtaining the first column position it contains plus the size multiplier * (cell size + spacing)
                cell_x = pos.x() + col_offset * (self.cell_size + self.horizontal_spacing)
                #get the cells y position similarly to the x but with vertical spacing between the rows
                cell_y = pos.y() + row_offset * (self.cell_size + self.vertical_spacing)

                #make sure the position is within grid boundaries
                if cell_x < self.left_right_margins or \
                        cell_y < self.top_bottom_margins or \
                        cell_x >= (self.cols * (self.cell_size + self.horizontal_spacing)) or \
                        cell_y >= (self.rows * (self.cell_size + self.vertical_spacing)):
                    continue  #continue if the cells are in a valid position else skip

                #save the cell in the positions dictionary
                self.positions[(cell_x, cell_y)] = widget
                #save the occupied cells for the current page
                occupied_cells.append((cell_x, cell_y))

    def is_position_available(self, pos, size_multiplier=(1, 1)):
        """check every grid cell occupied by size_multiplier dimensions,
            similar to the save function but just checks the position from the dictionary"""
        for row_offset in range(size_multiplier[1]):  # Vertical span
            for col_offset in range(size_multiplier[0]):  # Horizontal span
                #calculate the specific cell placement
                #same position calculation as the save widget position
                cell_x = pos.x() + col_offset * (self.cell_size + self.horizontal_spacing)
                cell_y = pos.y() + row_offset * (self.cell_size + self.vertical_spacing)

                #check bounds (grid is 4x7, with specific margins)
                if cell_x < self.left_right_margins or \
                        cell_y < self.top_bottom_margins or \
                        cell_x >= (self.cols * (self.cell_size + self.horizontal_spacing)) or \
                        cell_y >= (self.rows * (self.cell_size + self.vertical_spacing)):
                    return False  # Out of bounds

                #check if the position is already occupied using the position dictionary
                if (cell_x, cell_y) in self.positions:
                    return False  # The cell is occupied

        return True

    def get_snapped_position(self, pos, size_multiplier=(1, 1)):
        """snap the widget to the nearest grid alignment, respecting grid the grid margins."""
        #calculate the column and row index (e.g. row 0 , col 1)
        #column = (x position - left/right margins) / (113 <- accounts for spacing if widget spans multiple cols) returns a value from 0-6
        col = (pos.x() - self.left_right_margins) // (self.cell_size + self.horizontal_spacing)
        #similar to the column but with top and bottom margins and vertical spacing
        row = (pos.y() - self.top_bottom_margins) // (self.cell_size + self.vertical_spacing)

        #adjust to grid margins and return an int for index manipulation, since some widgets take multiple rows/cols
        col = max(0, min(col, self.cols - size_multiplier[0]))
        row = max(0, min(row, self.rows - size_multiplier[1]))

        #calculate the actual postion for placement with previously calculated values
        #snap_x = left/right margins + col index * (113)
        snapped_x = self.left_right_margins + col * (self.cell_size + self.horizontal_spacing)
        snapped_y = self.top_bottom_margins + row * (self.cell_size + self.vertical_spacing)

        return QPoint(snapped_x, snapped_y)

    def is_grid_full(self):
        """check if grid is full"""
        #returns a true value if the number of cells taken exceeds max cell count
        return len(self.widgets) >= 28

    def find_first_available_position(self, size_multiplier=(1, 1)):
        """find the first available position in the grid for a widget to be placed."""
        #loop through all rows and columns
        for row in range(self.rows - size_multiplier[1] + 1):  #adjust for row span
            for col in range(self.cols - size_multiplier[0] + 1):  #adjust for col span
                #calculate using the top-left corner of the widget position
                pos = QPoint(
                    self.left_right_margins + col * (self.cell_size + self.horizontal_spacing),
                    self.top_bottom_margins + row * (self.cell_size + self.vertical_spacing),
                )

                # Check if the calculated position is available
                if self.is_position_available(pos, size_multiplier=size_multiplier):
                    return pos

        return None  # No valid position found

    def remove_widget_position(self, widget):
        """remove all cells occupied by the given widget from the positions' dictionary if being dragged"""
        #get widget that is being dragged
        to_remove = [key for key, value in self.positions.items() if value == widget]
        for key in to_remove:
            #remove the widgets position, so it can be reoccupied by future widgets
            del self.positions[key]

    def remove_widget(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
            print(f"{widget} removed")
        self.remove_widget_position(widget)






