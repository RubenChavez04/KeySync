import os.path
from os.path import split

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea, QStackedWidget, QLabel, QPushButton, QVBoxLayout, QFrame, \
    QInputDialog

from gui_assets.buttons_sliders_etc.action_button import ActionButton
from gui_assets.buttons_sliders_etc.sidebar_button import SideBarToolButton
from gui_assets.buttons_sliders_etc.sidebar_label import SideBarLabel
from gui_assets.popups.add_action_popup import SelectFunctionPopup
from gui_assets.popups.select_page_popup import SelectPagePopup
from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.functions.getapps import get_apps, AppSelectionDialog


class ActionButtonsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setHorizontalSpacing(11)
        layout.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label = SideBarLabel(self, "Actions")
        label.setFixedHeight(25)
        layout.addWidget(label, 0, 0, 1, 4)
        #define buttons
        self.on_press_btn = ActionButton(
            self,
            "On-Press",
            "Edit actions on press",
        )
        self.on_press_btn.setChecked(True) #default to on press
        self.on_press_rel_btn = ActionButton(
            self,
            "On-Press \nRelease",
            "Edit actions on press release",
        )
        self.long_press_btn = ActionButton(
            self,
            "Long-Press",
            "Edit actions on long press",
        )
        self.long_press_rel_btn = ActionButton(
            self,
            "Long-Press \nRelease",
            "Edit actions on long press release",
        )
        #put buttons in an array, for button selection process
        self.buttons = [
            self.on_press_btn,
            self.on_press_rel_btn,
            self.long_press_btn,
            self.long_press_rel_btn
        ]
        for pos, button in enumerate(self.buttons):
            button.clicked.connect(lambda _, index=pos: self.button_selected(index))
            layout.addWidget(button, 1, pos)

        self.add_action_btn = SideBarToolButton(
            self,
            width=410,
            text= "+",
            tooltip="Add a new action"
        )
        self.add_action_btn.clicked.connect(self.show_function_menu)
        layout.addWidget(self.add_action_btn,2,0,1,4)

        #scroll area to show selected button_widget functions
        self.function_area = FunctionsContainer(self)
        layout.addWidget(self.function_area,3,0,1,4)


        self.setLayout(layout)
        self.button=None
        global_signal_dispatcher.selected_button.connect(self.update_widget)
        self.initial()

    def initial(self):
        for button in self.buttons:
            button.setEnabled(False)
        self.add_action_btn.setEnabled(False)
        self.function_area.hide()
        self.update()

    def button_selected(self, pos):
        selected_action_button = self.sender()
        for button in self.buttons:
            if button == selected_action_button:
                button.setChecked(True)
                button.setEnabled(True)
                self.function_area.change_index(pos)
            else:
                button.setChecked(False)
                button.setEnabled(True)

    def get_checked_action_key(self):
        for button in self.buttons:
            if button.isChecked():
                # Map the button to its corresponding function key
                if button.text() == "On-Press":
                    return "On_Press"
                elif button.text() == "On-Press \nRelease":
                    return "On_Press_Release"
                elif button.text() == "Long-Press":
                    return "Long_Press"
                elif button.text() == "Long-Press \nRelease":
                    return "Long_Press_Release"
        return None  # No button is currently checked

    def show_function_menu(self):
        action_type = self.get_checked_action_key()
        functions_list = ["Change Page", "Launch App", "Next Playlist", "Open URL"]
        dialog = SelectFunctionPopup(self, functions_list)
        if dialog.exec():
            selected_function = dialog.selected_function
            if selected_function == "Change Page":
                page_popup = SelectPagePopup(self.parent.parent.pages)
                if page_popup.exec():
                    selected_page_index = page_popup.selected_page_index
                    if action_type and self.button and selected_page_index is not None:
                        for action_types in ["On_Press", "On_Press_Release", "Long_Press", "Long_Press_Release"]:
                            for function in self.button.functions[action_types]:
                                if function.startswith(selected_function):
                                    print("Change Page action already exists for this button.")
                                    return
                        self.button.functions[action_type].append(f"Change Page:{selected_page_index}")

            elif selected_function == "Open URL":
                url_dialog = QInputDialog()
                url_dialog.setWindowTitle("Insert URL/Link")
                url_dialog.setLabelText("URL/Link")
                url_dialog.setCancelButtonText("Cancel")
                url_dialog.setOkButtonText("Add URL/Link")
                if url_dialog.exec() == QInputDialog.DialogCode.Accepted:
                    url = url_dialog.textValue()
                    self.button.functions[action_type].append(selected_function + ":" + url)
                else:
                    return

            elif selected_function == "Launch App":
                app = self.show_app_selection()
                if app and action_type and self.button:
                    self.button.functions[action_type].append(selected_function + ":" + app)

            elif selected_function == "Next Playlist":
                if action_type and self.button:
                    self.button.functions[action_type].append("spotify:next_playlist")
            elif selected_function:
                print(f"Function Selected: {selected_function}")
                if action_type and self.button:
                    self.button.functions[action_type].append(selected_function)
                    print(f"Added {selected_function} to {action_type}")
            self.update_widget(self.button)

    def show_app_selection(self):
        apps = get_apps()
        dialog = AppSelectionDialog(apps, self)
        if dialog.exec():
            try:
                selected_app = dialog.get_selected_app()
                if selected_app:
                    # Emit signal with selected app ID
                    print("Selected app: ", selected_app)
                    return selected_app
                else:
                    return None
            except Exception as e:
                print(f"Error occurred selecting app: {e}")

    def update_widget(self, button):
        self.button = button
        if button.__class__.__name__ == "ButtonWidget":
            for action_btn in self.buttons:
                action_btn.setEnabled(True)
            self.add_action_btn.setEnabled(True)
            self.function_area.update_container(button)
            self.function_area.show()
        else:
            for action_btn in self.buttons:
                action_btn.setEnabled(False)
            self.add_action_btn.setEnabled(False)
            self.function_area.hide()

class FunctionsContainer(QStackedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.button = None
        self.setFixedSize(410,270)
        self.setContentsMargins(0,0,0,0)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.opf_sa = FunctionsScrollArea(self)
        self.oprf_sa = FunctionsScrollArea(self)
        self.lpf_sa = FunctionsScrollArea(self)
        self.lprf_sa = FunctionsScrollArea(self)

        self.addWidget(self.opf_sa)
        self.addWidget(self.oprf_sa)
        self.addWidget(self.lpf_sa)
        self.addWidget(self.lprf_sa)

    def update_container(self, selected_button):
        self.button = selected_button

        if self.button.__class__.__name__ == "ButtonWidget":
            on_press_functions = self.button.functions["On_Press"]
            on_press_release_functions = self.button.functions["On_Press_Release"]
            long_press_functions = self.button.functions["Long_Press"]
            long_press_release_functions = self.button.functions["Long_Press_Release"]

            self.opf_sa.update_button_function_holders(on_press_functions, "On_Press")
            self.oprf_sa.update_button_function_holders(on_press_release_functions, "On_Press_Release")
            self.lpf_sa.update_button_function_holders(long_press_functions, "Long_Press")
            self.lprf_sa.update_button_function_holders(long_press_release_functions, "Long_Press_Release")

    def change_index(self, index):
        self.setCurrentIndex(index)

class FunctionsScrollArea(QWidget):
    def __init__(self,parent):
        super().__init__(parent)

        self.function_holders = []
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFixedSize(410,260)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.scroll_frame = QFrame()
        self.scroll_area.setWidgetResizable(True)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)  #

        self.scroll_frame.setLayout(self.layout)
        self.scroll_area.setWidget(self.scroll_frame)
        self.setStyleSheet("""
            QScrollArea {
                background-color: black;
                border-radius: 8px;
                padding:8px;
            }
            QFrame {
                background-color: black;
                border-radius: 8px;
            }
        """)

    def update_button_function_holders(self, functions, press_type):
        for function_holder in self.function_holders:
            function_holder.delete_me()
            self.layout.removeWidget(function_holder)
        self.function_holders.clear()
        for full_function in functions:
            function_holder = FunctionHolder(self, press_type, full_function)
            self.function_holders.append(function_holder)
            self.layout.addWidget(function_holder)

        self.update()
        self.scroll_frame.adjustSize()

    def delete_func_holder(self, func_holder):
        for holder in self.function_holders:
            if holder == func_holder:
                self.function_holders.remove(holder)
                holder.delete_me()

class FunctionHolder(QWidget):
    def __init__(self, parent, press_type, full_function):
        super().__init__(parent)
        self.full_function = full_function
        self.press_type = press_type
        split_full_function = full_function.split(":")
        print(split_full_function)
        function_name = split_full_function[0]
        self.parent = parent
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedSize(394, 35)
        params = split_full_function[1]
        if function_name == "Launch App":
            params = str(split_full_function[1]+":"+split_full_function[2])
            params = params.replace("\\","/")
            try:
                if os.path.exists(params):
                    params = os.path.basename(params)
            except Exception as e:
                print(f"Error:{e}")
        if function_name == "Open URL":
            for i, params in enumerate(split_full_function):
                if i >=1:
                    if i == 1:
                        params = split_full_function[1]
                    else:
                        params = params +":"+ split_full_function[i]


        self.label = QLabel(f"{function_name}: {params}", self)
        self.label.move(5,5)
        self.delete_func_btn = QPushButton(self)
        self.delete_func_btn.setFixedSize(30,30)
        self.delete_func_btn.move(360,2)
        self.delete_func_btn.setIconSize(self.delete_func_btn.size())
        self.delete_func_btn.setIcon(QIcon("gui_assets/gui_icons/trash_white.png"))
        self.delete_func_btn.clicked.connect(self.delete_function)
        self.setStyleSheet("""
            QWidget {
                Background: #303030;
                Border-radius: 5px;
            }
            QPushButton {
                background: transparent;
            }
            QLabel {
                background-color: transparent;
                font-weight: bold;
                font-size: 16px;
                color: white;
            }
        """)

    def delete_me(self):
        self.deleteLater()

    def delete_function(self):
        global_signal_dispatcher.remove_func_signal.emit(self.press_type,self.full_function)
        self.parent.delete_func_holder(self)

