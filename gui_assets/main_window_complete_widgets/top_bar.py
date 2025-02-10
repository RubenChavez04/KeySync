from PyQt6.QtWidgets import QWidget, QGridLayout

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

class PageTab(QWidget):
