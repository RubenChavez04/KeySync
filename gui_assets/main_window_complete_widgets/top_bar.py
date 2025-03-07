from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout

from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.tab_bar import TabBar
from gui_assets.main_window_complete_widgets.signal_dispatcher import global_signal_dispatcher


class TopBar(QWidget):
    add_widget_btn_pressed = pyqtSignal()
    def __init__(self, parent=None,):
        super().__init__(parent)
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setColumnStretch(0, 1)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.setVerticalSpacing(10)
        #main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        btn_layout = QGridLayout(self)
        btn_layout.setContentsMargins(0,0,0,0)
        btn_layout.setHorizontalSpacing(12)
        btn_layout.setVerticalSpacing(10)
        self.width = 191

        add_widget_btn = SideBarToolButton(
            self,
            text="+",
            tooltip="Add a new widget/button",
            width=self.width
        )
        change_background_btn = SideBarToolButton(
            self,
            text="Background",
            tooltip="Change the background of the page",
            width=self.width,
            font_size=15
        )
        preview_btn = SideBarToolButton(
            self,
            text="Preview",
            tooltip="Preview the page with functionality",
            width=self.width
        )
        settings_btn = SideBarToolButton(
            self,
            text="Settings",
            width=self.width
        )
        self.tab_bar = TabBar(self)

        add_widget_btn.clicked.connect(global_signal_dispatcher.add_widget_signal.emit)
        change_background_btn.clicked.connect(global_signal_dispatcher.change_page_background_signal.emit)


        btn_layout.addWidget(add_widget_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        btn_layout.addWidget(change_background_btn, 0, 1)
        btn_layout.addWidget(preview_btn, 0, 2)
        btn_layout.addWidget(settings_btn, 0, 3)
        main_layout.addLayout(btn_layout, 0, 0)
        main_layout.addWidget(self.tab_bar, 1, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

