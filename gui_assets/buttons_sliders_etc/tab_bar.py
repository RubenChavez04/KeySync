from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QPushButton, QLineEdit, QWidget, QVBoxLayout, QFrame, QScrollArea, QHBoxLayout


class RenamableTabButton(QPushButton):
    """Custom tab button class to handle double-click renaming."""
    renamed = pyqtSignal(str)  # Signal emitted when the tab is renamed

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #d9d9d9;
                border: 1px solid gray;
                border-radius: 5px;
                color: black;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: gray;
                color: white;
            }
        """)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to rename the tab."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.rename_tab()
        super().mouseDoubleClickEvent(event)

    def rename_tab(self):
        """Switch the button temporarily to a QLineEdit for renaming."""
        self.line_edit = QLineEdit(self.text(), self.parentWidget())
        self.line_edit.setFixedSize(self.size())
        self.line_edit.setStyleSheet("border: 1px solid gray;")
        self.line_edit.move(self.pos())
        self.line_edit.setFocus()
        self.line_edit.selectAll()

        def finish_renaming():
            # Set new text and emit a signal
            new_text = self.line_edit.text()
            self.setText(new_text)
            self.line_edit.deleteLater()
            self.show()  # Show the button again after renaming
            self.renamed.emit(new_text)

        self.line_edit.editingFinished.connect(finish_renaming)
        self.line_edit.show()
        #self.hide()  # Hide the button while editing

class CustomTabWidget(QWidget):
    """Custom tabs widget using an internal QFrame for containment."""
    tab_changed = pyqtSignal(int)  # Signal emitted when a tab index is changed

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout for the widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Internal frame containing all tab elements
        self.tabs_frame = QFrame(self)
        self.tabs_frame.setFrameShape(QFrame.Shape.Box)
        self.tabs_frame.setFixedSize(800,40)

        # Layout for the internal frame
        self.frame_layout = QVBoxLayout(self.tabs_frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(0)

        # Scroll area to contain the tabs
        self.scroll_area = QScrollArea(self.tabs_frame)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setViewportMargins(0, 0, 0, 0)

        # Container widget inside the scroll area
        self.tabs_widget = QWidget(self.scroll_area)
        self.tabs_layout = QHBoxLayout(self.tabs_widget)  # Horizontal layout for holding tab buttons
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(5)  # Small space between tabs
        self.tabs_layout.setAlignment(Qt.AlignmentFlag.AlignLeft |Qt.AlignmentFlag.AlignTop)  # Explicitly align tabs to the left
        self.tabs_widget.setLayout(self.tabs_layout)
        self.scroll_area.setWidget(self.tabs_widget)

        # Add the scroll area to the frame's layout
        self.frame_layout.addWidget(self.scroll_area)

        # Add the frame to the main widget layout
        self.main_layout.addWidget(self.tabs_frame)

        # Tab button parameters
        self.tab_buttons = []
        self.button_width = 100
        self.button_height = 20
        self.current_tab_index = 0  # Track currently active tab

        # Initialize the first tab and the add button
        self.init_first_tab()

        # Styling the frame
        self.tabs_frame.setStyleSheet("""
            QFrame {
                background-color: #303030;
                border: 2px solid #303030;
                border-radius: 8px; /* Rounded edges */
            }
        """)

        # Styling tabs_widget (the area where buttons are displayed)
        self.tabs_widget.setStyleSheet("""
            QWidget {
                background-color: #303030; /* Matches the QFrame color */
                border: none; /* Removes any border that creates dark areas */
            }
        """)

    def init_first_tab(self):
        """Initialize the first tab and the add button."""
        # Add the first tab
        first_tab = self.create_tab_button("Page 1")
        self.tabs_layout.addWidget(first_tab)
        self.tab_buttons.append(first_tab)

        # Add the "+" button
        add_button = self.create_add_button()
        self.tabs_layout.addWidget(add_button)

        # Set the first tab as active
        self.set_active_tab(first_tab)

    def create_tab_button(self, text: str) -> RenamableTabButton:
        """Create a button for the tab."""
        btn = RenamableTabButton(text, self)
        btn.setCheckable(True)
        btn.setFixedSize(self.button_width, self.button_height)
        btn.renamed.connect(self.handle_tab_renamed)  # Connect to renamed signal
        btn.clicked.connect(lambda: self.change_tab(self.tab_buttons.index(btn)))
        return btn

    def create_add_button(self) -> QPushButton:
        """Create the "+" button."""
        btn = QPushButton("+", self)
        btn.setFixedSize(self.button_width, self.button_height)
        btn.setStyleSheet("""
            QPushButton {
                background-color: lightgray;
                border: 1px solid darkgray;
                border-radius: 5px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: gray;
                color: white;
            }
        """)
        btn.clicked.connect(self.add_new_tab)
        return btn

    def set_active_tab(self, tab_button: QPushButton):
        """Set the given tab as active and deactivate others."""
        for button in self.tab_buttons:
            if button != tab_button:
                button.setChecked(False)  # Uncheck all other tabs
                button.repaint()  # Force repaint for update issues
        tab_button.setChecked(True)  # Check the currently active tab


    def add_new_tab(self):
        """Add a new tab dynamically."""
        new_tab = self.create_tab_button(f"Page {len(self.tab_buttons) + 1}")
        self.tab_buttons.append(new_tab)

        # Add the new tab to the layout before the "+" button
        self.tabs_layout.insertWidget(len(self.tab_buttons) - 1, new_tab)

        # Ensure proper layout updates, forcing UI to redraw the changes
        self.tabs_layout.update()
        self.tabs_frame.update()
        self.tabs_widget.update()

        # Notify the main window about the new tab (trigger page creation)
        self.tab_changed.emit(len(self.tab_buttons) - 1)

        # Scroll to the new tab (move to the far right)

        # Set the new tab as active
        self.set_active_tab(new_tab)

        # Force the scroll area to refresh/redraw
        self.scroll_area.update()
        self.scroll_area.ensureWidgetVisible(new_tab)
        self.scroll_to_tab(new_tab)

    def change_tab(self, index):
        """Change the active tab."""
        self.current_tab_index = index
        self.tab_changed.emit(index)
        self.set_active_tab(self.tab_buttons[index])
        self.tabs_layout.update()
        self.tabs_frame.update()
        self.tabs_widget.update()
        self.scroll_area.update()

    def handle_tab_renamed(self, new_name: str):
        """Handle the tab renaming (e.g., validation or logging)."""
        print(f"Tab renamed to: {new_name}")

    def scroll_to_tab(self, tab_button: QPushButton):
        """Ensure the scroll bar moves fully to the far right after a new tab is added."""
        scroll_bar = self.scroll_area.horizontalScrollBar()
        # Calculate the maximum scroll position dynamically
        # Force a scroll area update to ensure everything renders correctly
        self.scroll_area.update()
        self.tabs_widget.update()
        max_scroll_pos = scroll_bar.maximum()
        scroll_bar.setValue(max_scroll_pos)  # Fully move to the far-right edge

    def wheelEvent(self, event):
        """Allow mouse wheel to scroll tabs horizontally."""
        delta = event.angleDelta().y() / 8
        scroll_bar = self.scroll_area.horizontalScrollBar()
        if delta > 0:  # Scroll left
            scroll_bar.setValue(scroll_bar.value() - 20)
        else:  # Scroll right
            scroll_bar.setValue(scroll_bar.value() + 20)
        event.accept()