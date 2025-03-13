from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QGridLayout, QLabel

from gui_assets.buttons_sliders_etc.popup_title_bar import PopupTitleBar
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.title_bar import TitleBar


class AddWidgetPopup(QDialog):
    """popup window to select widget type"""
    def __init__(self, parent, grid):
        super().__init__(parent)
        self.setWindowTitle("Add Widget")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)   #make window frameless removing the titlebar
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.offset = None
        self.grid = grid    #parent grid
        self.layout = QVBoxLayout() #give the popup a layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background: transparent;")

        self.window = QWidget(self)
        self.titlebar = PopupTitleBar(self)
        self.window_layout = QVBoxLayout()
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window.setLayout(self.window_layout)
        self.window_layout.addWidget(self.titlebar, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.window)

        self.window.setLayout(self.window_layout)

        self.window.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #171717,
                    stop: 1 #2b2d30
                );
                border-radius: 8px;
        }""")

        self.container_layout = QGridLayout()
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.widget_btn_label = QLabel("Widget Button")
        self.widget_btn_label.setStyleSheet("""
            QLabel {
                background-color: None;
                font: bold 14px;
                color: white;
        }""")
        self.container_layout.addWidget(self.widget_btn_label,0,0,1,3, alignment=Qt.AlignmentFlag.AlignLeft)
        i=0
        for widget_type, size in [("1x1 Button", (1, 1)), ("2x2 Button", (2, 2)), ("Spotify Widget", (4, 2))]:
            i=i+1
            btn = SideBarToolButton(self, text=widget_type)
            btn.clicked.connect(lambda _, t=widget_type, s=size: self.add_widget(t, s))
            self.container_layout.addWidget(btn,1,i)

        self.window_layout.addLayout(self.container_layout)
        self.setLayout(self.layout)

    def add_widget(self, widget_type, size_multiplier):
        """add a widget to the grid"""
        self.grid.add_widget(widget_type, size_multiplier)
        self.close()


