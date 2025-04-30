from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel

from gui_assets.buttons_sliders_etc.QToggle import QToggle
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.sidebar_button_mini import SideBarToolButtonMini
from gui_assets.buttons_sliders_etc.sidebar_label import SideBarLabel
from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.weather_widget.weather_widget import WeatherWidget


class AppearanceWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

    # ----------Appearance Section----------#
        # Add a header for Appearance
        self.button = None
        appearance_header = SideBarLabel(self, "Appearance")
        appearance_header.setFixedHeight(25)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # add the header to the frame
        layout.addWidget(appearance_header, 0, 0,1,2)

        # add appearance section buttons
        self.add_label_button = SideBarToolButton(
            self,
            text="Add Label",
            tooltip="Add a label to your button",
            font_size= 12
        )
        self.add_label_button.clicked.connect(global_signal_dispatcher.add_label_signal.emit)

        self.variable_button = SideBarToolButton(
            self,
            text="(X)",
            tooltip="Add a variable to your button",
            italic=True
        )

        self.delete_button = SideBarToolButton(
            self,
            image_path="gui_assets/gui_icons/trash.ico",
            tooltip="Delete the button"
        )
        self.delete_button.clicked.connect(global_signal_dispatcher.delete_button_signal.emit)

        self.add_icon_button = SideBarToolButton(
            self,
            image_path="gui_assets/gui_icons/image.ico",
            tooltip="Add a image to your button"
        )
        self.add_icon_button.clicked.connect(global_signal_dispatcher.add_icon_signal.emit)

        self.change_color_button = SideBarToolButton(
            self,
            image_path="gui_assets/gui_icons/Color.ico",
            tooltip="Change the color of your button"
        )

        self.change_color_button.clicked.connect(global_signal_dispatcher.change_color_signal.emit)

        # set them in a specific layout

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setHorizontalSpacing(10)
        layout.addWidget(self.variable_button, 2, 1)
        layout.addWidget(self.add_label_button, 1, 0)
        layout.addWidget(self.delete_button, 3, 1)
        layout.addWidget(self.change_color_button, 2, 0)
        layout.addWidget(self.add_icon_button, 1, 1)
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

        layout.addLayout(state_layout, 3, 0)
        self.setLayout(layout)

        #update preview button appearance

        #get signal for selected button
        global_signal_dispatcher.selected_button.connect(self.selected_button)
        self.button = None
        self.delete_button.setDisabled(True)
        self.variable_button.setDisabled(True)
        self.add_icon_button.setDisabled(True)
        self.change_color_button.setDisabled(True)
        self.add_label_button.setDisabled(True)
        self.state_toggler.setDisabled(True)


    def selected_button(self, selected_button):
        print(selected_button.__class__.__name__)
        if str(selected_button.__class__.__name__) in ["SpotifyWidget","WeatherWidget"]:
            print(str(selected_button.__class__.__name__))
            print("disabled")
            self.delete_button.setDisabled(False)
            self.variable_button.setDisabled(True)
            self.add_icon_button.setDisabled(True)
            self.change_color_button.setDisabled(True)
            self.add_label_button.setDisabled(True)
            self.state_toggler.setDisabled(True)
        else:
            print("re-enabled")
            self.delete_button.setDisabled(False)
            self.variable_button.setDisabled(False)
            self.add_icon_button.setDisabled(False)
            self.change_color_button.setDisabled(False)
            self.add_label_button.setDisabled(False)
            self.state_toggler.setDisabled(False)
        self.update()