import PyQt6
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QDialog, QColorDialog, \
    QInputDialog, QFileDialog
import os
import re
from gui_assets.buttons_sliders_etc.QToggle import QToggle
from gui_assets.buttons_sliders_etc.button_preview import ButtonPreview
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.sidebar_button_mini import SideBarToolButtonMini
from gui_assets.buttons_sliders_etc.sidebar_label import SideBarLabel

from gui_assets.main_window_complete_widgets.signal_dispatcher import global_signal_dispatcher
signal_dispatcher = global_signal_dispatcher

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
        signal_dispatcher.selected_button.connect(self.selected_button)
        self.button = None
        add_label_button = SideBarToolButton(
            self,
            text="Add Label",
            tooltip="Add a label to your button",
            font_size= 12
        )
        add_label_button.clicked.connect(self.edit_button_text)
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
        delete_button.clicked.connect(self.delete_button)
        add_icon_button = SideBarToolButtonMini(
            self,
            image_path="gui_assets/gui_icons/image.ico",
            tooltip="Add a image to your button"
        )
        add_icon_button.clicked.connect(self.edit_icon)
        change_color_button = SideBarToolButtonMini(
            self,
            image_path="gui_assets/gui_icons/Color.ico",
            tooltip="Change the color of your button"
        )
        change_color_button.clicked.connect(self.edit_color)
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

    def selected_button(self, selected_button):
        self.button = selected_button

    def edit_button_text(self, selected_button):
        print("Edit button called")
        # When add label is pressed allow user to input new label
        if self.button:
            new_text, ok = QInputDialog.getText(self, "Edit Button Text", "Enter new text:")
            if ok and new_text:
                print(new_text)
                self.button.setText(new_text)
        else:
            print("No button selected for editing.")

    def edit_icon(self):
        image_path = self.chooseIcon()
        if self.button:
            if image_path:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    self.button.setText("")
                    scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    self.button.setIcon(QIcon(icon))
                    size = PyQt6.QtCore.QSize(100, 100)
                    self.button.setIconSize(size)
                else:
                    print("Failed to load image")
        else:
            print("No Button selected")

    def edit_color(self):
        if self.button:
            color = QColorDialog.getColor(initial=QColor(255, 255, 255), title="Select Color")
            if color.isValid():
                print(f"Hex color code: {color.name()}")
                self.button.setStyleSheet(re.sub(r'background-color:.*?;', f'background-color: {color.name()};', self.button.styleSheet()))

    def delete_button(self):
        if self.button:
            signal_dispatcher.update_position.emit(self.button)
            self.button.deleteLater()
            self.button = None

    def chooseIcon(self):
        options = QFileDialog.Option.DontUseNativeDialog
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        #change "" to downloads_folder to open downloads
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "","Image Files (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if file_path:
            return file_path
