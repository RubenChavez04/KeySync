from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QGridLayout, QLabel

from gui_assets.buttons_sliders_etc.popup_title_bar import PopupTitleBar
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton


class SelectFunctionPopup(QDialog):
    """Popup window to select a function."""

    def __init__(self, parent, functions_list):
        """
        Initialize the function selection popup.
        :param parent: Parent widget.
        :param functions_list: List of functions to display for selection.
        """
        super().__init__(parent)
        self.setWindowTitle("Select Function")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # Make window frameless, removing the titlebar
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.offset = None
        self.selected_function = None  # To store the selected function
        self.layout = QVBoxLayout()  # Main layout for the popup
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background: transparent;")

        # Create the main window container
        self.window = QWidget(self)
        self.titlebar = PopupTitleBar(self)
        self.window_layout = QVBoxLayout()
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window.setLayout(self.window_layout)
        self.window_layout.addWidget(self.titlebar, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.window)

        # Style for the window container
        self.window.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #171717,
                    stop: 1 #2b2d30
                );
                border-radius: 8px;
            }
        """)

        # Grid layout for buttons
        self.container_layout = QGridLayout()
        self.container_layout.setContentsMargins(10, 10, 10, 10)

        # Label for the popup
        self.function_label = QLabel("Select a Function")
        self.function_label.setStyleSheet("""
            QLabel {
                background-color: None;
                font: bold 14px;
                color: white;
            }
        """)
        self.container_layout.addWidget(self.function_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add buttons for each function in the provided list
        for i, function_name in enumerate(functions_list):
            btn = SideBarToolButton(self, text=function_name)
            btn.clicked.connect(lambda _, f=function_name: self.select_function(f))
            self.container_layout.addWidget(btn, i + 1, 0)

        self.window_layout.addLayout(self.container_layout)
        self.setLayout(self.layout)

    def select_function(self, function_name):
        """
        Handle the selection of a function.
        :param function_name: The name of the selected function.
        """
        self.selected_function = function_name
        print(f"Selected function: {function_name}")  # Debugging output
        self.accept()  # Close the dialog with success
