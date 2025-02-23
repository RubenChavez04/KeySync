from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout, QPushButton
import random

from gui_assets.main_window_complete_widgets.signal_dispatcher import global_signal_dispatcher
from gui_assets.popups.add_widget_popup import AddWidgetPopup


class Page(QWidget):
    def __init__(self, parent, image_path=None):
        random_hex1 = f"{random.randint(0x000000, 0xFFFFFF):06x}"
        random_hex2 = f"{random.randint(0x000000, 0xFFFFFF):06x}"
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.frame = QFrame(self)
        self.frame.setFixedSize(800, 480)   #frame size equal to the size of pi screen

        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(frame_layout)
        if image_path:
            self.frame.setStyleSheet(f"""
                QFrame {{
                    background-image: url({image_path});
                    background-repeat: no-repeat;
                    background-position: center;
                    border: 2px solid darkgray;
            }}""")
        else: #default to static background
            self.frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #{random_hex1},
                    stop: 1 #{random_hex2}
                );
                border: 2px solid darkgray;
            }}""")
        self.page_grid = PageGrid(self)
        frame_layout.addWidget(self.page_grid)

        layout.addWidget(self.frame)

        self.setLayout(layout)
    def show_add_widget_popup(self):
        self.popup = AddWidgetPopup(self, self.page_grid)
        self.popup.exec()


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
        self.cell_size = 100            # cell size is 100x100, so each button/widget is this,
                                        #  note that each widget will need size adjustments based on the spacings
                                        #  all widgets need a size_multiplier to keep track of the rows and columns each take
        self.vertical_spacing = 20      # spacing between rows
        self.horizontal_spacing = 13    # spacing between columns
        self.top_bottom_margins = 10    # margins for the top and bottom of frame
        self.left_right_margins = 11    # margins for the left and right of frame

        self.setFixedSize(800,480)      # set size to frame size

        self.widgets = []   #list of added widgets
        self.positions = {} #dictionary to track widgets

    def add_widget(self, widget_type, size_multiplier = (1,1), position = None):
        available_pos = self.find_first_available_position() if not position else position

        #add all widgets we create here (e.g. Spotify
        if available_pos:
            if widget_type == "Spotify":
                #button for now
                widget = ButtonWidget(self, self.cell_size, size_multiplier, available_pos)
            else:
                widget = ButtonWidget(self, self.cell_size, size_multiplier, available_pos)

            widget.move(available_pos)
            self.widgets.append(widget)
            self.save_widget_position(widget, available_pos)
            widget.show()

            if self.is_grid_full():         # check if grid is full
                self.grid_full.emit(True)   # if full emit true signal
                pass
            else:
                self.grid_full.emit(False)  # else emit false signal
        else:
            print("Page is full!")

    def save_widget_position(self, widget, pos):
        """Save positions for all blocks occupied by the widget."""
        size_multiplier = widget.size_multiplier
        occupied_positions = []  # Keep track of all occupied cells

        for row_offset in range(size_multiplier[1]):  # Vertical span
            for col_offset in range(size_multiplier[0]):  # Horizontal span
                cell_x = pos.x() + col_offset * (self.cell_size + self.horizontal_spacing)
                cell_y = pos.y() + row_offset * (self.cell_size + self.vertical_spacing)

                # Ensure the position is within bounds
                if cell_x < self.left_right_margins or \
                        cell_y < self.top_bottom_margins or \
                        cell_x >= (self.cols * (self.cell_size + self.horizontal_spacing)) or \
                        cell_y >= (self.rows * (self.cell_size + self.vertical_spacing)):
                    continue  # Skip invalid positions

                # Save the cell in the positions dictionary
                self.positions[(cell_x, cell_y)] = widget
                occupied_positions.append((cell_x, cell_y))

        print(f"Widget saved at positions: {occupied_positions}")

    def is_position_available(self, pos, size_multiplier=(1, 1)):
        """Check every grid cell occupied by size_multiplier dimensions."""
        for row_offset in range(size_multiplier[1]):  # Vertical span
            for col_offset in range(size_multiplier[0]):  # Horizontal span
                # Calculate the specific cell
                cell_x = pos.x() + col_offset * (self.cell_size + self.horizontal_spacing)
                cell_y = pos.y() + row_offset * (self.cell_size + self.vertical_spacing)

                # Check bounds (grid is 4x7, with specific margins)
                if cell_x < self.left_right_margins or \
                        cell_y < self.top_bottom_margins or \
                        cell_x >= (self.cols * (self.cell_size + self.horizontal_spacing)) or \
                        cell_y >= (self.rows * (self.cell_size + self.vertical_spacing)):
                    return False  # Out of bounds

                # Check if the position is already occupied
                if (cell_x, cell_y) in self.positions:
                    return False  # The cell is occupied

        return True

    def get_snapped_position(self, pos, size_multiplier=(1, 1)):
        """Snap the widget to the nearest grid alignment, respecting grid boundaries."""
        col = (pos.x() - self.left_right_margins) // (self.cell_size + self.horizontal_spacing)
        row = (pos.y() - self.top_bottom_margins) // (self.cell_size + self.vertical_spacing)

        # Adjust to grid boundaries
        col = max(0, min(col, self.cols - size_multiplier[0]))
        row = max(0, min(row, self.rows - size_multiplier[1]))

        snapped_x = self.left_right_margins + col * (self.cell_size + self.horizontal_spacing)
        snapped_y = self.top_bottom_margins + row * (self.cell_size + self.vertical_spacing)

        return QPoint(snapped_x, snapped_y)

    def is_grid_full(self):
        """check if grid is full"""
        #returns a true value if the number of cells taken exceeds max cell count
        return len(self.widgets) >= 28

    def find_first_available_position(self, size_multiplier=(1, 1)):
        """Find the first available position in the grid for a widget to be placed."""
        # Loop through all rows and columns
        for row in range(self.rows - size_multiplier[1] + 1):  # Adjust for vertical span
            for col in range(self.cols - size_multiplier[0] + 1):  # Adjust for horizontal span
                # Calculate the top-left corner of the position
                pos = QPoint(
                    self.left_right_margins + col * (self.cell_size + self.horizontal_spacing),
                    self.top_bottom_margins + row * (self.cell_size + self.vertical_spacing),
                )

                # Check if the calculated position is available
                if self.is_position_available(pos, size_multiplier=size_multiplier):
                    return pos

        return None  # No valid position found

    def remove_widget_position(self, widget):
        """Remove all cells occupied by the given widget from the positions dictionary."""
        to_remove = [key for key, value in self.positions.items() if value == widget]
        for key in to_remove:
            del self.positions[key]

        print(f"Removed positions for widget: {to_remove}")


class ButtonWidget(QPushButton):
    """draggable button widget with custom sizing parameters, users can select button size"""
    def __init__(self, parent, cell_size, size_multiplier=(1, 1), position=None):
        super().__init__(parent)
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.pos()
            self.last_valid_position = self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            new_pos = self.mapToParent(event.pos() - self.startPos)
            self.move(self.parent.get_snapped_position(new_pos, self.size_multiplier))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Step 1: Get the snapped position
            snapped_pos = self.parent.get_snapped_position(self.pos(), self.size_multiplier)
            print(f"Snapped Position: {snapped_pos}")

            # Step 2: Temporarily remove old positions
            self.parent.remove_widget_position(self)

            # Step 3: Check if the snapped position is valid
            if self.parent.is_position_available(snapped_pos, self.size_multiplier):
                print(f"Position valid, moving to {snapped_pos}")
                self.move(snapped_pos)
                self.parent.save_widget_position(self, snapped_pos)  # Save the new position
                self.last_valid_position = snapped_pos  # Update last valid position
            else:
                print(f"Position invalid, reverting to {self.last_valid_position}")
                self.parent.save_widget_position(self, self.last_valid_position)  # Restore old position
                self.move(self.last_valid_position)  # Revert to old position


