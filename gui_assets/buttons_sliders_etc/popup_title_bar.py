from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QLabel, QToolButton


class PopupTitleBar(QWidget):
    # constructor
    def __init__(self, parent):
        # calls constructor
        super().__init__(parent)
        self._drag_pos = None  # Used to store the drag position relative to the window

        # set a fixed size of the title bar
        self.setFixedHeight(30)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # sets the layout with a horizontal container
        title_bar_layout = QHBoxLayout(self)
        # no margins since we want objects to get close to the ends
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        # spacing between objects
        title_bar_layout.setSpacing(4)

        # create a title for the window, this gets the window title from setWindowTitle
        # which gets initialized in the main window
        self.title = QLabel(f"{self.__class__.__name__}", self)
        # align the title in the center
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font: bold 14px; 
                margin-left: 60px;
                color: white;
            }
        """)

        # set the title text to match the parent window's title
        if title := self.window().windowTitle():
            self.title.setText(title)

        # add the title to the title bar
        title_bar_layout.addWidget(self.title, stretch=1)

        # close button
        self.close_button = QToolButton(self)
        # give the close button a custom icon
        close_icon = QIcon()
        # give the close button a icon file
        close_icon.addFile("gui_assets/gui_icons/Close-256.ico")
        self.close_button.setIcon(close_icon)
        #if close is pressed close the program
        self.close_button.clicked.connect(self.window().close)

        # sdd close and minimize buttons to the title bar
        # this is set so keyboard inputs don't mess with the buttons, only gets mouse input
        self.close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # size the buttons
        self.close_button.setFixedSize(QSize(25, 25))
        # style the buttons, specifically transparent background for a cleaner look
        self.close_button.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
            }
        """)
        #add widget to the title bar
        title_bar_layout.addWidget(self.close_button)

    #-----------------------------------------------Methods-----------------------------------------------#
    # Handle dragging the window using the custom title bar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            #calculates the offset between the mouse cursor position and the top left corner of the window
            #This is used because we need to calculate where to position the window when we move
            # it from the title bar
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            #this just accepts the event, in this case the title bar has been pressed in an empty area
            event.accept()

    def mouseMoveEvent(self, event):
        # this checks to see if the title bar is still being pressed and makes sure the
        # dragging logic has been initialized
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            # this calculates the new position of the window
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            # this sets the window position
            self.window().move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        # checks to see if the title bar is being pressed if not set to the new position
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            event.accept()