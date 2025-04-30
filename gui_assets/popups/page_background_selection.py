import os
import shutil
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog,
    QScrollArea, QWidget, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize
from gui_assets.signal_dispatcher import global_signal_dispatcher
from pathlib import Path



class ChangePageBackgroundDialog(QDialog):
    def __init__(self, project_folder="pi_assets/page_backgrounds"):
        super().__init__()

        # Setup UI
        self.setWindowTitle("Change Page Background")
        self.setGeometry(200, 200, 600, 200)

        self.project_folder = project_folder
        self.init_project_folder()

        self.layout = QVBoxLayout(self)

        self.import_button = QPushButton("Import Images")
        self.import_button.clicked.connect(self.import_images)
        self.layout.addWidget(self.import_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.hbox_layout = QHBoxLayout(self.scroll_widget)
        self.hbox_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

        # Load existing images when the dialog opens
        self.load_existing_images()

    def init_project_folder(self):
        """make sure the background directory exists and set the directory for os"""
        if not os.path.exists(self.project_folder): #make sure path exists
            os.makedirs(self.project_folder) #set the path with os

    def load_existing_images(self):
        """load images from previous imports from directory"""
        for file_name in os.listdir(self.project_folder): #for each file in backgrounds directory
            if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".gif")): #ensure they are images
                image_path = os.path.join(self.project_folder, file_name) #get the image path
                image_path = image_path.replace("\\","/")
                self.add_image_button(image_path) #add the image button

    def import_images(self):
        """open the qfiledialog to allow import of images"""
        file_dialog = QFileDialog() #define dialog
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles) #sets it to existing files on PC
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.svg *.gif)") #filter for only images on the dialog

        if file_dialog.exec(): #while the dialog is executed
            selected_files = file_dialog.selectedFiles() #get selected files
            print(f"import images: {selected_files}")
            self.save_and_display_images(selected_files) #save selected files


    def save_and_display_images(self, file_paths):
        """save any newly imported images and """
        for file_path in file_paths: #for each selected file from import
            file_name = os.path.basename(file_path) #get the file name
            dest_path = os.path.join(self.project_folder, file_name) #append directory
            dest_path = dest_path.replace("\\","/")
            print(f"first dest {dest_path}")

            #copy image to background directory only if it doesn't exist to prevent copies
            if not os.path.exists(dest_path):
                shutil.copy(file_path, dest_path) #copy file to background directory
            print(f"save and display{dest_path}")
            self.add_image_button(dest_path) #add the newly imported image as a button

    def add_image_button(self, image_path):
        """adds the image as a push button so users can preview which image to select"""
        print(f"add image button {image_path}")
        button = QPushButton()
        pixmap = QPixmap(image_path)

        #parameters so preview is accurate to size of background
        page_width, page_height = 800, 480
        aspect_ratio = pixmap.width() / pixmap.height()

        #scale image down for preview
        preview_width = int(page_width * 0.25)
        preview_height = int(preview_width / aspect_ratio)

        #resize the pixmap of button and set image as button icon
        resized_pixmap = pixmap.scaled(preview_width, preview_height)
        button.setIcon(QIcon(resized_pixmap))
        button.setIconSize(QSize(preview_width, preview_height))
        button.setFixedSize(preview_width, preview_height)

        #lamda function to always connect buttons to set page background function
        button.clicked.connect(lambda: self.set_page_background(image_path))

        #add the button to scroll area
        self.hbox_layout.addWidget(button)

    def set_page_background(self, image_path):
        """emit signal to change background and close dialog"""
        global_signal_dispatcher.image_selected_signal.emit(image_path) #emit image path
        self.accept()  #close dialog after selection

