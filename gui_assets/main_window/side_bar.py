from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont
from PyQt6.QtWidgets import (QWidget, QSizePolicy, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
                             QGridLayout, QToolButton, QGraphicsDropShadowEffect)
from gui_assets.buttons_sliders_etc.QToggle import QToggle
#imports for testing widget
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.sidebar_button_mini import SideBarToolButtonMini
from gui_assets.buttons_sliders_etc.sidebar_label import SideBarLabel
from gui_assets.widgets.action_buttons_widget import ActionButtonsWidget
from gui_assets.widgets.appearance_widget import AppearanceWidget


class ShadowFX(QGraphicsDropShadowEffect):
    def __init__(self, parent):
        super().__init__(parent)
        self.setBlurRadius(15)
        self.setOffset(0)
        self.setColor(QColor(0, 0, 0, 150))

class SideBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        appearance_shadow = ShadowFX(self)
        actions_shadow = ShadowFX(self)
    #frame setup
        frame = QFrame(self)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setStyleSheet("""
        QFrame {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #bfbfbf,
                stop: 1 #737373
            );
            border-radius: 8px;
        }""")
        #set size
        frame.setFixedHeight(540)
        frame.setFixedWidth(430)  # Sidebar fixed width
        frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        #frame layout setup
        frame_layout = QGridLayout()
        frame.setLayout(frame_layout)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        frame_layout.setSpacing(10)
        # Styling the sidebar to have a gray background
        appearance_widget = AppearanceWidget(frame)
        appearance_widget.setGraphicsEffect(appearance_shadow)
        frame_layout.addWidget(appearance_widget,0,0)

        action_buttons = ActionButtonsWidget(frame)
        action_buttons.setGraphicsEffect(actions_shadow)
        frame_layout.addWidget(action_buttons,1,0)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Window")
        self.setStyleSheet("""
        QMainWindow {
            background: black;
        }""")
        self.test_layout = QVBoxLayout()
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(self.test_layout)
        self.side_bar = SideBar(self)
        self.test_layout.addWidget(self.side_bar)


if __name__ == "__main__":
    app = QApplication([])
    window = TestWindow()
    window.show()
    sys.exit(app.exec())