from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QPushButton, QLineEdit, QWidget, QVBoxLayout, QFrame, QScrollArea, QHBoxLayout


class TabButton(QPushButton):
    """Custom tab button class to handle double-click renaming."""
    renamed = pyqtSignal(str)  #signal emitted when the tab is renamed

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
        if event.button() == Qt.MouseButton.LeftButton: #if left click twice
            self.rename_tab() #call rename method
        super().mouseDoubleClickEvent(event)

    def rename_tab(self):
        """Switch the button temporarily to a QLineEdit for renaming."""
        line_edit = QLineEdit(self.text(), self.parentWidget())
        line_edit.setFixedSize(self.size()) #set the line edit to the size of the button
        line_edit.setStyleSheet("border: 1px solid gray;")
        line_edit.move(self.pos())
        line_edit.setFocus()
        line_edit.selectAll()

        def finish_renaming():
            #set new text and emit a signal
            new_text = line_edit.text()
            self.setText(new_text)
            line_edit.deleteLater()
            self.show()  #show the button again after renaming
            self.renamed.emit(new_text) #emit signal for text change

        line_edit.editingFinished.connect(finish_renaming)
        line_edit.show()

class TabBar(QWidget):
    tab_changed = pyqtSignal(int)  #signal emitted when a tab index is changed

    def __init__(self, parent=None):
        super().__init__(parent)

        #main layout for the widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        #internal frame containing all tab elements
        self.tabs_frame = QFrame(self)
        self.tabs_frame.setFrameShape(QFrame.Shape.Box)
        self.tabs_frame.setFixedSize(800,40)

        #layout for the internal frame
        self.frame_layout = QVBoxLayout(self.tabs_frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(0)

        #scroll area to contain the tabs
        self.scroll_area = QScrollArea(self.tabs_frame)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setViewportMargins(0, 0, 0, 0)

        #container widget inside the scroll area
        self.tabs_widget = QWidget(self.scroll_area)
        self.tabs_layout = QHBoxLayout(self.tabs_widget)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(5)
        self.tabs_layout.setAlignment(Qt.AlignmentFlag.AlignLeft |Qt.AlignmentFlag.AlignTop)
        self.tabs_widget.setLayout(self.tabs_layout)
        self.scroll_area.setWidget(self.tabs_widget)

        #add the scroll area to the frame's layout and frame to main layout
        self.frame_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.tabs_frame)

        #tab button parameters
        self.tab_buttons = []
        self.button_width = 100
        self.button_height = 20
        self.current_tab_index = 0  #track currently active tab

        #initialize the tab bar
        self.init_first_tab()

        #styling the frame containing everything
        self.tabs_frame.setStyleSheet("""
            QFrame {
                background-color: #303030;
                border: 2px solid #303030;
                border-radius: 8px; /* Rounded edges */
            }
        """)

        #styling tabs_widget (the area where buttons are displayed)
        self.tabs_widget.setStyleSheet("""
            QWidget {
                background-color: #303030; /* Matches the QFrame color */
                border: none; /* Removes any border that creates dark areas */
            }
        """)

    def init_first_tab(self):
        """Initialize the first tab and the add button."""
        #add the first tab
        first_tab = self.create_tab_button("Page 1")
        self.tabs_layout.addWidget(first_tab)
        self.tab_buttons.append(first_tab)
        #add the add button
        add_button = self.create_add_button()
        self.tabs_layout.addWidget(add_button)
        # Set the first tab as active
        self.set_active_tab(first_tab)

    def create_tab_button(self, text: str) -> TabButton:
        """Create a tab button"""
        btn = TabButton(text, self)
        btn.setCheckable(True)
        #set button size
        btn.setFixedSize(self.button_width, self.button_height)
        #switch to the newly created tab
        btn.clicked.connect(lambda: self.change_tab(self.tab_buttons.index(btn)))
        return btn #return the tab button

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
        return btn #return the add button

    def set_active_tab(self, tab_button: QPushButton):
        """set the given tab as active and deactivate others."""
        for button in self.tab_buttons:
            if button != tab_button: #if tab is not active run the following
                button.setChecked(False)  #uncheck all other tabs
                button.repaint()  #need this to ensure tabs have unchecked style
        tab_button.setChecked(True)  #check the active tab

    def add_new_tab(self):
        """add a new tab when "+" button is clicked."""
        #call create_tab
        new_tab = self.create_tab_button(f"Page {len(self.tab_buttons) + 1}")
        #add new tab to index
        self.tab_buttons.append(new_tab)
        # Add the new tab to the layout before the "+" button
        self.tabs_layout.insertWidget(len(self.tab_buttons) - 1, new_tab)
        #send a signal to main_gui for a page to be created
        self.tab_changed.emit(len(self.tab_buttons) - 1)
        #set the new tab as the active tab
        self.set_active_tab(new_tab)
        #set the scroll tab to far right
        self.scroll_area.update()
        self.scroll_area.ensureWidgetVisible(new_tab)
        self.scroll_to_tab(new_tab)

    def change_tab(self, index):
        """Change the active tab."""
        #get tab index
        self.current_tab_index = index
        #emit tab changed signal for parent widget
        self.tab_changed.emit(index)
        #set the active tab with method
        self.set_active_tab(self.tab_buttons[index])

    def scroll_to_tab(self, tab_button: QPushButton):
        """move the scroll bar to the right (used for after adding a new tab)"""
        scroll_bar = self.scroll_area.horizontalScrollBar()
        #set the scroll bar position to its maximum
        max_scroll_pos = scroll_bar.maximum() #get max scroll value
        scroll_bar.setValue(max_scroll_pos)  #fully move to the far-right

    def wheelEvent(self, event):
        """Allow mouse wheel to scroll tabs horizontally."""
        #return the amount scrolled from mouse scroll wheel
        delta = event.angleDelta().y() / 8
        #set scroll bar to scroll bar from parent
        scroll_bar = self.scroll_area.horizontalScrollBar()
        if delta > 0:  #wheel scroll left
            #set the scrollbars new value each scroll, -20
            scroll_bar.setValue(scroll_bar.value() - 20)
        else:  #wheel scroll right
            #opposite as left
            scroll_bar.setValue(scroll_bar.value() + 20)
        event.accept()