from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea, QVBoxLayout

from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton


class TopBar(QWidget):
    def __init__(self, parent=None,):
        super().__init__(parent)
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setHorizontalSpacing(10)


        add_widget_btn = SideBarToolButton(self)
        change_background_btn = SideBarToolButton(self)


        self.setLayout(layout)

class TabBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(30)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(Tab(self))
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        tab_layout = QGridLayout()
        main_tab = Tab(self)

    def add_tab(self):


class Tab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

