from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout

from gui_assets.buttons_sliders_etc.action_button import ActionButton
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.sidebar_label import SideBarLabel
from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.functions.getapps import get_apps, AppSelectionDialog


class ActionButtonsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setHorizontalSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label = SideBarLabel(self, "Actions")
        label.setFixedHeight(25)
        layout.addWidget(label, 0, 0, 1, 4)
        #define buttons
        on_press_btn = ActionButton(
            self,
            "On-Press",
            "Edit actions on press",
        )
        on_press_btn.setChecked(True) #default to on press
        on_press_rel_btn = ActionButton(
            self,
            "On-Release",
            "Edit actions on press release",
        )
        long_press_btn = ActionButton(
            self,
            "Long-Press",
            "Edit actions on long press",
        )
        long_press_rel_btn = ActionButton(
            self,
            "Long-Press \nRelease",
            "Edit actions on long press release",
        )
        #put buttons in an array, for button selection process
        self.buttons = [on_press_btn, on_press_rel_btn, long_press_btn, long_press_rel_btn]
        pos = 0
        for button in self.buttons:
            button.clicked.connect(self.button_selected)
            layout.addWidget(button,1,pos)
            pos = pos + 1
        add_action_btn = SideBarToolButton(
            self,
            width=410,
            text= "+",
            tooltip="Add a new action"
        )
        add_action_btn.clicked.connect(self.show_app_selection)
        layout.addWidget(add_action_btn,2,0,1,4)
        self.setLayout(layout)
        self.button=None
        global_signal_dispatcher.selected_button.connect(self.selected_button)

    def button_selected(self):
        selected_button = self.sender()
        for button in self.buttons:
            if button == selected_button:
                button.setChecked(True)
                button.setEnabled(True)
            else:
                button.setChecked(False)
                button.setEnabled(True)

    def show_app_selection(self):
        apps = get_apps()
        dialog = AppSelectionDialog(apps, self)
        if dialog.exec():
            selected_app = dialog.get_selected_app()
            if selected_app:
                # Emit signal with selected app ID
                print("Selected app: ", selected_app)
                self.button.appID = selected_app

    def selected_button(self, selected_button):
        self.button = selected_button
