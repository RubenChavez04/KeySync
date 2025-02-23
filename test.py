import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt, QPoint


LAYOUT_FILE = "layout.json"  # JSON file for persistent storage


class DraggableWidget(QPushButton):
    """Generic draggable widget (for buttons, small elements)"""
    def __init__(self, widget_type, parent, grid_size, size_multiplier=(1, 1), position=None):
        super().__init__(widget_type, parent)
        self.parent = parent
        self.grid_size = grid_size
        self.size_multiplier = size_multiplier
        self.widget_type = widget_type
        self.setFixedSize(grid_size * size_multiplier[0], grid_size * size_multiplier[1])
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
            snapped_pos = self.parent.get_snapped_position(self.pos(), self.size_multiplier)
            if self.parent.is_position_available(snapped_pos, self, self.size_multiplier):
                self.move(snapped_pos)
                self.parent.save_layout()  # Auto-save on move
            else:
                self.move(self.last_valid_position)


class SpotifyWidget(QWidget):
    """A fixed Spotify widget with specific grid size (2 rows × 4 columns)"""
    def __init__(self, parent, grid_size, position=None):
        super().__init__(parent)
        self.parent = parent
        self.grid_size = grid_size
        self.size_multiplier = (4, 2)  # 2 rows × 4 columns
        self.setFixedSize(grid_size * self.size_multiplier[0], grid_size * self.size_multiplier[1])
        self.setStyleSheet("background-color: #1DB954; border: 2px solid black;")
        if position:
            self.move(position)


class MacroDeckGrid(QWidget):
    """Main widget grid for adding and managing draggable buttons/widgets"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.screen_width = 800
        self.screen_height = 480
        self.rows = 4
        self.cols = 8

        self.padding = 10
        self.spacing = 5

        self.grid_size = (self.screen_width - 2 * self.padding - (self.cols - 1) * self.spacing) // self.cols
        self.setFixedSize(self.screen_width, self.screen_height - 50)

        self.setStyleSheet("background-color: #222; border: 2px solid #444;")

        self.widgets = []
        self.positions = {}  # Dictionary to track occupied positions
        self.load_layout()  # Load saved layout on startup

    def add_widget(self, widget_type, size_multiplier=(1, 1), position=None):
        """Find the first available position and add a new widget."""
        available_pos = self.find_first_available_position(size_multiplier) if not position else position

        if available_pos:
            if widget_type == "Spotify":
                widget = SpotifyWidget(self, self.grid_size, available_pos)
            else:
                widget = DraggableWidget(   self, self.grid_size, size_multiplier, available_pos)

            widget.move(available_pos)
            self.widgets.append(widget)
            self.save_widget_position(widget, available_pos)
            widget.show()

            self.save_layout()  # Auto-save on add

            if self.is_grid_full():
                self.main_window.add_button.setDisabled(True)
        else:
            print(f"No space available for {widget_type}!")

    def save_widget_position(self, widget, pos):
        """Store widget positions to prevent overlapping"""
        self.positions[(pos.x(), pos.y())] = widget

    def is_position_available(self, pos, ignore_widget=None, size_multiplier=(1, 1)):
        """Check if a given position is available in the grid, considering multi-cell widgets."""
        return all(
            (pos.x(), pos.y()) not in self.positions for _ in range(size_multiplier[0] * size_multiplier[1])
        )

    def get_snapped_position(self, pos, size_multiplier):
        """Snap widgets to the nearest grid position"""
        col = (pos.x() - self.padding) // (self.grid_size + self.spacing)
        row = (pos.y() - self.padding) // (self.grid_size + self.spacing)
        return QPoint(
            self.padding + col * (self.grid_size + self.spacing),
            self.padding + row * (self.grid_size + self.spacing)
        )

    def save_layout(self):
        """Save the layout to a JSON file"""
        layout_data = [
            {"type": widget.widget_type if isinstance(widget, DraggableWidget) else "Spotify",
             "x": widget.x(), "y": widget.y(), "size": widget.size_multiplier}
            for widget in self.widgets
        ]

        with open(LAYOUT_FILE, "w") as file:
            json.dump(layout_data, file, indent=4)

    def load_layout(self):
        """Load the layout from a JSON file"""
        if os.path.exists(LAYOUT_FILE):
            with open(LAYOUT_FILE, "r") as file:
                try:
                    layout_data = json.load(file)
                    for widget_data in layout_data:
                        self.add_widget(widget_data["type"], tuple(widget_data["size"]), QPoint(widget_data["x"], widget_data["y"]))
                except json.JSONDecodeError:
                    print("Error reading layout file. Resetting layout.")

    def remove_widget(self, widget):
        """Remove a widget from the grid"""
        if widget in self.widgets:
            self.widgets.remove(widget)
            self.save_layout()  # Auto-save after removal

    def find_first_available_position(self, size_multiplier):
        """Find the first available position in the grid"""
        for row in range(self.rows - size_multiplier[1] + 1):
            for col in range(self.cols - size_multiplier[0] + 1):
                pos = QPoint(
                    self.padding + col * (self.grid_size + self.spacing),
                    self.padding + row * (self.grid_size + self.spacing),
                )
                if self.is_position_available(pos, size_multiplier=size_multiplier):
                    return pos

    def is_grid_full(self):
        pass


class MainWindow(QWidget):
    """Main Application Window"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Macro Deck")
        self.setFixedSize(800, 480)
        layout = QVBoxLayout()

        self.deck = MacroDeckGrid(self)

        self.add_button = QPushButton("Add Widget", self)
        self.add_button.clicked.connect(self.show_add_dialog)

        layout.addWidget(self.add_button)
        layout.addWidget(self.deck)
        self.setLayout(layout)

    def show_add_dialog(self):
        """Open the Add Widget dialog"""
        dialog = AddWidgetDialog(self, self.deck)
        dialog.exec()


class AddWidgetDialog(QDialog):
    """Popup window to select widget type"""
    def __init__(self, parent, deck):
        super().__init__(parent)
        self.setWindowTitle("Add Widget")
        self.setFixedSize(200, 150)
        self.deck = deck

        layout = QVBoxLayout()
        for text, size in [("1x1 Button", (1, 1)), ("2x2 Button", (2, 2)), ("Spotify Widget (2x4)", (4, 2))]:
            btn = QPushButton(text, self)
            btn.clicked.connect(lambda _, t=text, s=size: self.add_widget(t, s))
            layout.addWidget(btn)

        self.setLayout(layout)

    def add_widget(self, widget_type, size_multiplier):
        """Add a widget to the grid"""
        self.deck.add_widget(widget_type, size_multiplier)
        self.close()



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
