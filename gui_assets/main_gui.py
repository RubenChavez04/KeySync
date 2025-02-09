from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QFrame, QSizePolicy, QGridLayout,
    QGraphicsDropShadowEffect
)
from gui_assets.title_bar import TitleBar
from gui_assets.main_window.side_bar import SideBar


#was working on grid layout to include spacers and all the contents
#need spacers since shadow fx don't appear on the margins for some reason

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Give our window a title
        self.setWindowTitle("KeySync")
        # Set the window size
        self.resize(1280, 580)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        side_bar_shadow = QGraphicsDropShadowEffect(self)
        side_bar_shadow.setBlurRadius(15)
        side_bar_shadow.setOffset(0)
        side_bar_shadow.setColor(QColor(0, 0, 0, 100))

        # Central widget for the main window
        main_window = QWidget(self)
        main_window.setObjectName("Container")
        main_window.setStyleSheet(
            """#Container {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #093d70,
                    stop: 1 #737373
                );
                border-radius: 8px;
            }"""
        )
        # Layout for the central widget
        main_window_layout = QGridLayout()
        # set margins to zero since spacer items allow for better shadowing
        main_window_layout.setContentsMargins(10, 0, 10, 10)
        #set spacing between items
        main_window_layout.setSpacing(10)

        #add custom title bar
        title_bar = TitleBar(self)
        title_bar_layout = QVBoxLayout()
        title_bar_layout.setContentsMargins(0,0,0,0)
        title_bar_layout.setSpacing(0)
        title_bar_layout.addWidget(title_bar)
        #add the title bar at the top
        #main_window_layout.addWidget(title_bar,0,0,1,2, Qt.AlignmentFlag.AlignTop)


        # Sidebar widget (Add this on the left of the frame)
        side_bar = SideBar(self)  # Sidebar needs the preview button
        side_bar.setGraphicsEffect(side_bar_shadow)
        main_window_layout.addWidget(side_bar, 0, 0, 2, 1)

        # Frame widget (Add this on the right of the sidebar)
        frame = QFrame()
        frame.setFixedSize(800, 480)
        frame.setObjectName("frame")
        frame.setFrameShape(QFrame.Shape.WinPanel)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame.setStyleSheet("""
            frame {
                background-color: #f0f0f0; 
                border: 0px solid #ccc;
                border-radius: 0px;
            }
        """)
        #frame.setGraphicsEffect(shadow)
        main_window_layout.addWidget(frame, 1, 1) #stretch=1

        # Add side_and_frame_layout to the workspace layout

        # Set the layout for the central widget
        title_bar_layout.addLayout(main_window_layout)
        main_window.setLayout(title_bar_layout)
        self.setCentralWidget(main_window)





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