from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QDialog

from gui_assets.buttons_sliders_etc.QToggle import QToggle
from gui_assets.buttons_sliders_etc.button_preview import ButtonPreview
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.sidebar_button_mini import SideBarToolButtonMini
from gui_assets.buttons_sliders_etc.sidebar_label import SideBarLabel


class AppearanceWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

    # ----------Appearance Section----------#
        # Add a header for Appearance
        appearance_header = SideBarLabel(self, "Appearance")
        appearance_header.setFixedHeight(25)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # add the header to the frame
        self.button_preview = ButtonPreview(self)
        layout.addWidget(self.button_preview, 1, 0)
        layout.addWidget(appearance_header, 0, 0,1,2)
        # add appearance section buttons
        add_label_button = SideBarToolButton(
            self,
            text="Add Label",
            tooltip="Add a label to your button",
            font_size= 12
        )
        variable_button = SideBarToolButtonMini(
            self,
            text="(X)",
            tooltip="Add a variable to your button",
            italic=True
        )
        delete_button = SideBarToolButtonMini(
            self,
            image_path="gui_assets/gui_icons/trash.ico",
            tooltip="Delete the button"
        )
        add_icon_button = SideBarToolButtonMini(
            self,
            image_path="gui_assets/gui_icons/image.ico",
            tooltip="Add a image to your button"
        )
        change_color_button = SideBarToolButtonMini(
            self,
            image_path="gui_assets/gui_icons/Color.ico",
            tooltip="Change the color of your button"
        )
        # set them in a specific layout
        appearance_button_layout = QGridLayout()
        appearance_button_layout.setContentsMargins(0, 0, 0, 0)
        appearance_button_layout.setSpacing(8)
        appearance_button_layout.setHorizontalSpacing(10)
        appearance_button_layout.addWidget(variable_button, 2, 1)
        appearance_button_layout.addWidget(add_label_button, 0, 0, 1, 2)
        appearance_button_layout.addWidget(delete_button, 2, 0)
        appearance_button_layout.addWidget(change_color_button, 1, 0)
        appearance_button_layout.addWidget(add_icon_button, 1, 1)
    # ----------State Section----------#
        self.state_toggler = QToggle(self)
        self.state_toggler.setFixedHeight(25)
        self.state_toggler.setToolTip("Change the appearance based on state")
        self.state_toggler.setStyleSheet("""
                QToggle{
                    qproperty-bg_color:#ff4d4d;
                    qproperty-circle_color:#DDF;
                    qproperty-active_color:#57965c;
                    qproperty-disabled_color:#4a4a4a;
                    qproperty-text_color:#A0F;
                }
                QToolTip {
                    font: bold 14px;
                    background-color: transparent;
                    border-radius: 10px;
                    color: white;
                }""")
        state_layout = QHBoxLayout()
        state_layout.setContentsMargins(0, 0, 0, 0)
        state_layout.setSpacing(4)
        state_label = QLabel("State:", self)
        state_label.setFixedWidth(60)
        state_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        state_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        state_layout.addWidget(state_label)
        state_layout.addWidget(self.state_toggler)
        # add the button layout to the main sidebar layout
        # Preview Button Header & Button

        appearance_button_layout.addLayout(state_layout, 3, 0, 1, 2)
        layout.addLayout(appearance_button_layout, 1, 1)
        self.setLayout(layout)

        self.state_toggler.stateChanged.connect(self.update_button_state)

    def update_button_state(self, state):
        if self.state_toggler.isChecked():
            self.button_preview.update_style("On")
        else:
            self.button_preview.update_style("Off")





