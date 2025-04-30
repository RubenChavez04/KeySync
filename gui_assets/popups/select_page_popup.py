from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QGridLayout, QLabel, QPushButton

from gui_assets.buttons_sliders_etc.popup_title_bar import PopupTitleBar
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton


class SelectPagePopup(QDialog):
    def __init__(self, parent, pages):
        """
        Popup for selecting a page, styled similarly to SelectFunctionPopup.

        :param parent: Parent widget.
        :param pages: List of pages (Page objects or dict containing page attributes).
        """
        super().__init__(parent)
        self.setWindowTitle("Select Page")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # Make the window frameless
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.offset = None
        self.selected_page_index = None  # To store the selected page index

        # Main Layout for the Popup
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background: transparent;")  # Ensure transparency for frameless

        # Create the main window container
        self.window = QWidget(self)
        self.titlebar = PopupTitleBar(self)  # Custom title bar for the popup
        self.window_layout = QVBoxLayout()
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window.setLayout(self.window_layout)
        self.window_layout.addWidget(self.titlebar, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.window)

        # Style for the window
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

        # Grid Layout for Pages
        self.container_layout = QGridLayout()
        self.container_layout.setContentsMargins(10, 10, 10, 10)

        # Add a Label
        self.page_label = QLabel("Select a Page")
        self.page_label.setStyleSheet("""
            QLabel {
                background-color: None;
                font: bold 14px;
                color: white;
            }
        """)
        self.container_layout.addWidget(self.page_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add Buttons for Pages
        for i, page in enumerate(pages):
            page_name = page.name if hasattr(page, 'name') else f"Page {i + 1}"  # Handle unnamed pages
            btn = SideBarToolButton(self, text=page_name)
            btn.clicked.connect(lambda _, idx=i: self.select_page(idx))  # Pass the index on button press
            self.container_layout.addWidget(btn, i + 1, 0)

        self.window_layout.addLayout(self.container_layout)
        self.setLayout(self.layout)

    def select_page(self, page_index):
        """
        Handle the selection of a page.

        :param page_index: The index of the selected page.
        """
        self.selected_page_index = page_index
        print(f"Selected Page Index: {page_index}")  # Debugging output
        self.accept()  # Close the dialog with success
