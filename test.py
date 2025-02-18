from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt, QPoint


#####THIS IS JUST CHAT CODE FOR LATER REFERENCE
#gives us an idea on the events and defs needed for our application process
#got bored and wanted to test to see if setting a grid size of 4x8 was doable and it is
class DraggableButton(QPushButton):
    def __init__(self, text, parent, grid_size, size_multiplier=(1, 1)):
        super().__init__(text, parent)
        self.parent = parent
        self.grid_size = grid_size
        self.size_multiplier = size_multiplier
        self.setFixedSize(grid_size * size_multiplier[0], grid_size * size_multiplier[1])
        self.startPos = None
        self.last_valid_position = None  # Store last valid position

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.pos()
            self.last_valid_position = self.pos()  # Save last position

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            new_pos = self.mapToParent(event.pos() - self.startPos)
            self.move(self.parent.get_snapped_position(new_pos, self.size_multiplier))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            snapped_pos = self.parent.get_snapped_position(self.pos(), self.size_multiplier)
            if self.parent.is_position_available(snapped_pos, self, self.size_multiplier):
                self.move(snapped_pos)
                self.parent.save_widget_position(self, snapped_pos)
            else:
                self.move(self.last_valid_position)  # Snap back to last valid position


class AddWidgetDialog(QDialog):
    """Popup window to select widget size"""
    def __init__(self, parent, deck):
        super().__init__(parent)
        self.setWindowTitle("Add Widget")
        self.setFixedSize(200, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.deck = deck  # Explicitly pass the MacroDeckGrid instance
        self.setStyleSheet(
            """QDialog {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #093d70,
                    stop: 1 #737373
                );
                border-radius: 8px;
            }"""
        )
        layout = QVBoxLayout()

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        btn_small = QPushButton("1x1 Button", self)
        btn_small.clicked.connect(lambda: self.add_widget((1, 1)))

        btn_large = QPushButton("2x2 Button", self)
        btn_large.clicked.connect(lambda: self.add_widget((2, 2)))

        layout.addWidget(btn_small)
        layout.addWidget(btn_large)
        self.setLayout(layout)

    def add_widget(self, size_multiplier):
        """Find an empty spot and add the widget"""
        if not self.deck.is_grid_full():
            self.deck.add_widget(f"Btn {len(self.deck.widgets) + 1}", size_multiplier)
            self.close()
        else:
            self.status_label.setText("Grid is full!")

    def setCentralWidget(self, window):
        pass


class MacroDeckGrid(QWidget):
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
        self.positions = {}

    def add_widget(self, label, size_multiplier=(1, 1)):
        """Find the first available position and add a new widget."""
        available_pos = self.find_first_available_position(size_multiplier)
        if available_pos:
            btn = DraggableButton(label, self, self.grid_size, size_multiplier)
            btn.move(available_pos)
            self.widgets.append(btn)
            self.save_widget_position(btn, available_pos)
            btn.show()

            # Disable adding if grid is full
            if self.is_grid_full():
                self.main_window.add_button.setDisabled(True)
        else:
            print("No space available!")

    def find_first_available_position(self, size_multiplier):
        """Find the first available grid position for the given size multiplier."""
        for row in range(self.rows - size_multiplier[1] + 1):
            for col in range(self.cols - size_multiplier[0] + 1):
                pos = QPoint(
                    self.padding + col * (self.grid_size + self.spacing),
                    self.padding + row * (self.grid_size + self.spacing),
                )
                if self.is_position_available(pos, size_multiplier=size_multiplier):
                    return pos
        return None

    def is_position_available(self, pos, ignore_widget=None, size_multiplier=(1, 1)):
        """Check if a given position is available in the grid, considering multi-cell widgets."""
        for widget, stored_pos in self.positions.items():
            if widget == ignore_widget:
                continue

            widget_col = stored_pos[0] // (self.grid_size + self.spacing)
            widget_row = stored_pos[1] // (self.grid_size + self.spacing)
            widget_width = widget.size_multiplier[0]
            widget_height = widget.size_multiplier[1]

            # Check if any part of the new button overlaps existing ones
            new_col = pos.x() // (self.grid_size + self.spacing)
            new_row = pos.y() // (self.grid_size + self.spacing)

            if (
                (new_col < widget_col + widget_width and new_col + size_multiplier[0] > widget_col) and
                (new_row < widget_row + widget_height and new_row + size_multiplier[1] > widget_row)
            ):
                return False  # Overlapping detected!

        return True

    def is_grid_full(self):
        """Check if all available spots are occupied."""
        total_slots = self.rows * self.cols
        return len(self.widgets) >= total_slots

    def get_snapped_position(self, pos, size_multiplier=(1, 1)):
        """Calculate the nearest valid grid position while ensuring the widget fits in bounds."""
        max_col = self.cols - size_multiplier[0]
        max_row = self.rows - size_multiplier[1]

        col = max(0, min(max_col, round((pos.x() - self.padding) / (self.grid_size + self.spacing))))
        row = max(0, min(max_row, round((pos.y() - self.padding) / (self.grid_size + self.spacing))))

        x = self.padding + col * (self.grid_size + self.spacing)
        y = self.padding + row * (self.grid_size + self.spacing)

        return QPoint(x, y)

    def save_widget_position(self, widget, pos):
        """Store widget positions (can be saved to JSON later)"""
        self.positions[widget] = (pos.x(), pos.y())
        print("Updated Positions:", self.positions)


class MainWindow(QWidget):
    """Main UI with an 'Add Widget' button"""
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
        """Open the add widget dialog"""
        dialog = AddWidgetDialog(self, self.deck)
        dialog.exec()


# Running the Application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
