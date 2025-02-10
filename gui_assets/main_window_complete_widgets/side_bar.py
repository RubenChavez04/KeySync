from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QSizePolicy, QFrame,
                             QGridLayout, QGraphicsDropShadowEffect)

from gui_assets.buttons_sliders_etc.shadow_fx import ShadowFX
from gui_assets.widgets.action_buttons_widget import ActionButtonsWidget
from gui_assets.widgets.appearance_widget import AppearanceWidget


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