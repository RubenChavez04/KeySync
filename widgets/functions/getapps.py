import os
import subprocess
import winreg

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QFileDialog


def get_apps2():
    # Get the directory of the current Python script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the relative path to your .ps1 script inside the project
    ps1_file_path = os.path.join(script_dir, "scripts", "getapps_ps1.ps1")  # Example: /scripts/example.ps1

    # Run the PowerShell script
    result = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps1_file_path],
                            capture_output=True, text=True)

    # Handle the result
    if result.returncode == 0:
        print("PowerShell script executed successfully!")
        print(result.stdout)
    else:
        print(f"Error running script: {result.stderr}")


def get_apps():
    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    apps_list = []

    for uninstall_key in uninstall_keys:
        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                with winreg.OpenKey(hive, uninstall_key) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            try:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                try:
                                    main_exe = winreg.QueryValueEx(sub_key, "DisplayIcon")[0]
                                    if "uninstall" in main_exe.lower() or not main_exe.endswith(".exe"):
                                        install_location = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                                        if install_location:
                                            main_exe = os.path.join(install_location, display_name + ".exe")
                                except FileNotFoundError:
                                    install_location = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                                    if install_location:
                                        main_exe = os.path.join(install_location, display_name + ".exe")
                                apps_list.append((display_name, main_exe))
                            except FileNotFoundError:
                                pass
            except FileNotFoundError:
                continue
    return sorted(apps_list, key=lambda x: x[0].lower())


class AppSelectionDialog(QDialog):
    def __init__(self, apps, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Application")
        layout = QVBoxLayout()
        self.selected_custom_file = None
        # Create list widget with app names
        self.list_widget = QListWidget()
        self.list_widget.addItems([app[0] for app in apps])  # Show only app names
        layout.addWidget(self.list_widget)

        # Add selection button
        choose_exe_button = QPushButton("Open File Explorer")
        choose_exe_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(choose_exe_button)

        select_button = QPushButton("Select")
        select_button.clicked.connect(self.accept)
        layout.addWidget(select_button)

        self.setLayout(layout)
        self.apps = apps  # Store full app data

        self.setStyleSheet("""
                    QListWidget {
                        background-color: lightgray;
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
        if self.selected_custom_file:  # Check if a custom file was selected
            return self.selected_custom_file
        if self.list_widget.currentItem():
            index = self.list_widget.currentRow()
            return self.apps[index][1]  # Return the AppID of selected item

    def open_file_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters(["Executable Files (*.exe)","Shortcuts (*.lnk)","All Files (*.*)"])

        if file_dialog.exec():
            self.selected_custom_file = file_dialog.selectedFiles()[0]  # Set selected file path
            print(f"Selected file: {self.selected_custom_file}")
        else:
            print("No file selected")
