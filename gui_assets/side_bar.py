from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QApplication

#imports for testing widget
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

class SideBar(QWidget):
    def __init__(self, parent, button_preview):
        super().__init__(parent)
        self.setFixedWidth(200)  # Sidebar fixed width
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Styling the sidebar to have a gray background
        self.setStyleSheet("""
            #SideBar {
                background-color: #d3d3d3;  /* Light gray background */
                border-right: 1px solid #a0a0a0;  /* Add subtle border to differentiate */
            }
        """)

        # Sidebar Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ---- Appearance Section ---- #
        # Add a header for Appearance
        layout.addWidget(QLabel("<b>Appearance:</b>", self))


        # Change Icon Button
        change_icon_button = QPushButton("Change Icon", self)
        layout.addWidget(change_icon_button)

        # Preview Button Header & Button
        layout.addWidget(QLabel("<b>Preview Button:</b>"))
        layout.addWidget(button_preview)

        # Spacer for flexible layout
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class ButtonPreview(QPushButton):
    def __init__(self, parent=None):
        super().__init__("Preview Button", parent)
        self.setCheckable(True)  # To allow "On/Off" state toggle
        self.setFixedSize(50, 50)
        self.update_style("Off")

    def update_style(self, state):
        # Update button style based on state
        colors = {
            "On": "background-color: #4CAF50; color: white;",
            "Off": "background-color: #f44336; color: white;"
        }
        self.setStyleSheet(f"QPushButton {{{colors[state]}}}")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Window")
        test_layout = QVBoxLayout()
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(test_layout)
        self.side_bar = SideBar(self, ButtonPreview(self))
        test_layout.addWidget(self.side_bar)


if __name__ == "__main__":
    app = QApplication([])
    window = TestWindow()
    window.show()
    sys.exit(app.exec())