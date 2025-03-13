import os
import re

from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout, QPushButton
import random

from gui_assets.main_window_complete_widgets.signal_dispatcher import global_signal_dispatcher
from gui_assets.popups.add_widget_popup import AddWidgetPopup


class Page(QWidget):
    def __init__(self, parent, image_path="page_backgrounds/wallpaper2.jpg"):

        super().__init__(parent)
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

    def show_add_widget_popup(self):
        self.popup = AddWidgetPopup(self, self.page_grid)
        self.popup.exec()

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
            random_hex1 = f"{random.randint(0x000000, 0xFFFFFF):06x}"
            random_hex2 = f"{random.randint(0x000000, 0xFFFFFF):06x}"
            self.frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #{random_hex1},
                        stop: 1 #{random_hex2}
                    );
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

    def add_widget(self, widget_type, size_multiplier = (1,1), position = None):
        """add a widget to the grid, gets called in the pop up"""
        available_pos = self.find_first_available_position() if not position else position

        #add all widgets we create here (e.g. Spotify
        if available_pos:
            if widget_type == "Spotify":
                #button for now
                widget = ButtonWidget(self, self.cell_size, size_multiplier, available_pos)
            else:
                widget = ButtonWidget(self, self.cell_size, size_multiplier, available_pos)

            widget.move(available_pos)  #move the widget to the first available position
            self.widgets.append(widget) #add widget to widget list
            self.save_widget_position(widget, available_pos)    #save the widgets position to stop widget overlapping
            widget.show()   #show the widget, updates just the widget

            if self.is_grid_full():         # check if grid is full
                self.grid_full.emit(True)   # if full emit true signal, to be used for disabling add widget button
                pass
            else:
                self.grid_full.emit(False)  # else emit false signal
        else:
            print("Page is full!")

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


class ButtonWidget(QPushButton):
    """draggable button widget with custom sizing parameters, users can select button size"""
    def __init__(self, parent, cell_size, size_multiplier=(1, 1), position=None):
        #needed a size multiplier for determining col and row span [0] is col [1] is row
        super().__init__(parent)
        #define parent grid
        self.parent = parent
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier
        if size_multiplier == (1,1):
            self.setFixedSize(cell_size, cell_size)
        else:
            self.setFixedSize(cell_size * size_multiplier[0] + (size_multiplier[0]*13)-13, #width = 100 * (how much columns to take) + spacing
                              cell_size * size_multiplier[1] + (size_multiplier[1]*20)-20)
        self.startPos = None
        self.last_valid_position = position if position else QPoint(0, 0)
        self.move(self.last_valid_position)
        self.setStyleSheet(
            f"QPushButton {{border-radius: 8px;background-color: #f0f0f0;border: None;}} QPushButton:hover {{ background-color: #cccccc;}}")
        global_signal_dispatcher.selected_button.connect(self.showSelected)

    def mouseDoubleClickEvent(self,event):
        """Handle double-click to rename the tab."""
        if event.button() == Qt.MouseButton.LeftButton: #if left click twice
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

    def showSelected(self, selected_button):
        if self == selected_button:
            self.setStyleSheet(re.sub(r'border:.*?;', 'border: 4px solid green;', self.styleSheet()))
        else:
            self.setStyleSheet(re.sub(r'border:.*?;', 'border: None;', self.styleSheet()))


