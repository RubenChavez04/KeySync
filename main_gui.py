from PyQt6.QtCore import Qt, QEvent, QSize
from PyQt6.QtGui import QPalette, QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QLabel,
    QStyle, QWidget, QVBoxLayout, QToolBar, QToolButton, )
#We have no idea where this came from, it was causing an error but im afraid to delete it in case we need it for something


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeySync")
        self.resize(1600, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        central_widget = QWidget()
        # This container holds the window contents, so we can style it.
        central_widget.setObjectName("Container")
        #found a gradient background i liked =)
        central_widget.setStyleSheet(
            """#Container {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #5E005E stop:1 #0101A7);
            border-radius: 8px;
            }"""
        )
        self.title_bar = TitleBar(self)

        work_space_layout = QVBoxLayout()
        work_space_layout.setContentsMargins(11, 11, 11, 11)
        work_space_layout.addWidget(QLabel("Hello, World!", self))

        central_widget_layout = QVBoxLayout()
        central_widget_layout.setContentsMargins(0, 0, 0, 0)
        central_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        central_widget_layout.addWidget(self.title_bar)
        central_widget_layout.addLayout(work_space_layout)

        central_widget.setLayout(central_widget_layout)
        self.setCentralWidget(central_widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Set the initial position of the cursor relative to the top-left corner of the window
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()  # Mark the event as handled

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            # Calculate the new position of the window
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)  # Move the window
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None  # Reset the drag position when the mouse is released
            event.accept()


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        #creates an initial position variable, used for when user moves window around

        # Sets the layout with a horizontal container
        title_bar_layout = QHBoxLayout(self)
        # these lines set margins and spacing
        title_bar_layout.setContentsMargins(3, 3, 3, 3)
        title_bar_layout.setSpacing(2)

        #create a title for the window
        self.title = QLabel(f"{self.__class__.__name__}", self)
        #align the title in the top center of the window
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #style the title, set font, font size, etc...
        self.title.setStyleSheet("""
            Qlabel {
            font-size: 10px; 
            margin-left:48px;}
            """)
        if title := self.window().windowTitle():
            self.title.setText(title)
        #add the title to the title bar
        title_bar_layout.addWidget(self.title)

        #minimize button
        #declares minimize button as Qt tool bar button
        self.min_button = QToolButton(self)
        #sets the icon of the tool button
        min_icon = QIcon()
        min_icon.addFile(".venv/GUI_Icons/minimize_icon.svg")
        self.min_button.setIcon(min_icon)
        #minimizes the window when clicked
        self.min_button.clicked.connect(self.window().showMinimized)

        #close button
        self.close_button = QToolButton(self)
        #sets the icon of the close button
        close_icon = QIcon()
        close_icon.addFile(".venv/GUI_Icons/Close-256.ico")
        self.close_button.setIcon(close_icon)

        #closes the window when clicked
        self.close_button.clicked.connect(self.window().close)

        #add buttons to the title bar now
        buttons = [self.min_button, self.close_button]
        for button in buttons:
            #Sets the focus policy, in our case no focus means the button will not receive keyboard focus
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            #sixe of the buttons
            button.setFixedSize(QSize(25,25))
            #actually add the button
            title_bar_layout.addWidget(button)
            button.setStyleSheet("""
                QToolButton {
                border: none;
                background: transparent;
                padding: 0px;
                }
            """)
