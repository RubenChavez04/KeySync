from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QLinearGradient, QColor, QPainter
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QToolButton,
    QWidget, QFrame, QSizePolicy, QSpacerItem, QComboBox, QLineEdit, QGridLayout,
    QFileDialog, QPushButton
)
from gui_assets.title_bar import TitleBar
from gui_assets.side_bar import SideBar, ButtonPreview

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Give our window a title
        self.setWindowTitle("KeySync")
        # Set the window size
        self.resize(1200, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Central widget for the main window
        central_widget = QWidget(self)
        central_widget.setObjectName("Container")
        central_widget.setStyleSheet(
            """#Container {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1d242e,
                    stop: 1 #000000
                );
                border-radius: 8px;
            }"""
        )

        # Custom title bar
        self.title_bar = TitleBar(self)

        # Layout for the central widget
        central_widget_layout = QVBoxLayout()
        central_widget_layout.setContentsMargins(0, 0, 0, 0)  # No margins for fullscreen effect

        # Add the title bar at the top
        central_widget_layout.addWidget(self.title_bar)

        # Workspace layout for the rest of the content
        work_space_layout = QVBoxLayout()
        work_space_layout.setContentsMargins(11, 11, 11, 11)

        # Layout to position the sidebar alongside the frame
        side_and_frame_layout = QHBoxLayout()
        side_and_frame_layout.setContentsMargins(0, 0, 0, 0)  # No margins for proper alignment

        # Sidebar widget (Add this on the left of the frame)
        self.button_preview = ButtonPreview(self)  # Create a button preview
        self.side_bar = SideBar(self, self.button_preview)  # Sidebar needs the preview button
        side_and_frame_layout.addWidget(self.side_bar)

        # Frame widget (Add this on the right of the sidebar)
        self.frame = QFrame()
        self.frame.setFixedSize(800, 480)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0; 
                border: 0px solid #ccc;
            }
        """)
        side_and_frame_layout.addWidget(self.frame, stretch=1)

        # Add side_and_frame_layout to the workspace layout
        work_space_layout.addLayout(side_and_frame_layout)

        # Add the workspace to the central widget layout
        central_widget_layout.addLayout(work_space_layout)

        # Set the layout for the central widget
        central_widget.setLayout(central_widget_layout)
        self.setCentralWidget(central_widget)





#class Button(QWidget):
#    def __init__(self, appName):



#        def
# thinking about making the frame its own class to simplify main window code
# possibly do this for all elements that get added to the main window just to keep
# things a bit more simplified, easier to add, and easier to debug
# class Frame(QFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.setFrameShape(QFrame.Shape.StyledPanel)
#         self.setFrameShadow(QFrame.Shadow.Raised)