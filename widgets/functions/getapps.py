import os
from PyQt6.QtCore import Qt
import winreg
import csv
import subprocess
import wmi

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QInputDialog, QFileDialog, QMessageBox

apps_dict = {}

def get_largest_exe_in_subfolders(folder):
    largest_exe = None
    largest_size = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".exe"):
                exe_path = os.path.join(root, file)
                file_size = os.path.getsize(exe_path)
                if file_size > largest_size:
                    largest_exe = exe_path
                    largest_size = file_size
    return largest_exe

def get_apps():
    global apps_dict
    if apps_dict:
        return sorted([(name, path) for name, path in apps_dict.items() if path.endswith(".exe")], key=lambda x: x[0].lower())

    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for uninstall_key in uninstall_keys:
        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                with winreg.OpenKey(hive, uninstall_key) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            try:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                install_location = winreg.QueryValueEx(sub_key, "InstallLocation")[0].strip('"')
                                if install_location:
                                    top_level_exes = [
                                        file for file in os.listdir(install_location)
                                        if file.endswith(".exe") and "uninstall" not in file.lower() and file.lower() not in ["unins000.exe", "update.exe"]
                                    ]
                                    if top_level_exes:
                                        for file in top_level_exes:
                                            exe_path = os.path.join(install_location, file)
                                            if display_name not in apps_dict:
                                                apps_dict[display_name] = exe_path
                                    else:
                                        largest_exe = get_largest_exe_in_subfolders(install_location)
                                        if largest_exe:
                                            apps_dict[display_name] = largest_exe
                            except (FileNotFoundError, KeyError, OSError):
                                pass
            except FileNotFoundError:
                continue

    return [(name, path) for name, path in apps_dict.items() if path.endswith(".exe")]

class AppSelectionDialog(QDialog):
    def __init__(self, apps, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Application")
        layout = QVBoxLayout()

        # Create list widget with app names
        self.list_widget = QListWidget()
        self.list_widget.addItems([app[0] for app in apps])  # Show only app names
        layout.addWidget(self.list_widget)

        # Add selection button
        select_button = QPushButton("Select Application")
        select_button.clicked.connect(self.accept)
        layout.addWidget(select_button)

        # Add button to add a new app
        add_button = QPushButton("Add New Application")
        add_button.clicked.connect(self.add_new_app)
        layout.addWidget(add_button)

        self.setLayout(layout)
        self.apps = apps  # Store full app data

        self.setStyleSheet("""
                    QListWidget {
                        background-color: lightgray;
                        alternate-background-color: darkgray;
                    }
                    QDialog {
                        background-color: #f0f0f0;  # Match the style of the rest of the project
                    }
                    QPushButton {
                        background-color: #dcdcdc;
                        border: 1px solid #a9a9a9;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #c0c0c0;
                    }
                """)

    def get_selected_app(self):
        if self.list_widget.currentItem():
            index = self.list_widget.currentRow()
            return self.apps[index][1]  # Return the AppID of selected item
        return None

    def add_new_app(self):
        # Get display name
        display_name, ok = QInputDialog.getText(self, "Add New App", "Enter display name:")
        if ok and display_name:
            # Get file path
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Executable", "",
                                                       "Executable Files (*.exe);;All Files (*)")
            if file_path and file_path.endswith(".exe"):
                global apps_dict
                apps_dict[display_name] = file_path  # Add new app to the dictionary
                self.apps.append((display_name, file_path))
                self.apps = sorted(self.apps, key=lambda x: x[0].lower())  # Re-sort the list
                self.list_widget.clear()
                self.list_widget.addItems([app[0] for app in self.apps])
            else:
                QMessageBox.warning(self, "Invalid File", "Please select a valid executable file.")
