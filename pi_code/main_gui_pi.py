from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedLayout
from plumbum.cli import switch

from pi_code.page_pi import Page  # Ensure the client-facing Page is imported
from pi_code.signal_dispatcher_pi import pi_signal_dispatcher
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set basic window properties
        self.setFixedSize(800, 480)  # Screen size for the Pi
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        # Stacked Layout for managing pages
        self.page_container = QStackedLayout()
        self.page_container.setContentsMargins(0, 0, 0, 0)  # No margins
        self.pages = []  # List to keep track of loaded pages
        central_layout.addLayout(self.page_container)
        self.restore_all_pages()
        pi_signal_dispatcher.change_page_signal.connect(self.switch_or_add_page)

    def add_new_page(self):
        page = Page(self)  # Create a new Page instance
        self.pages.append(page)
        self.page_container.addWidget(page)

    def switch_or_add_page(self,index, restore=False):
        """When a tab is changed or added, switch to page that is indexed with tab, else add a new page"""
        if not restore:
            self.blockSignals(False)
        if restore:
            self.blockSignals(True)
        if index >= len(self.pages): #check if page exists with current amount of tabs
            self.add_new_page() #add a new page
            print(index)
        self.page_container.setCurrentWidget(self.pages[index]) #go to page indexed with tab

    def restore_all_pages(self, filepath="saved_pages.json"):
        """
        Restore all pages and their widgets from a JSON file.
        """
        try:
            with open(filepath, "r") as file:
                all_pages_data = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading file {filepath}: {e}")
            return

        #validate the JSON data
        if not all_pages_data.get("pages"):
            print(f"Error: Missing 'pages' key in {filepath}")
            return

        try:

            #get all data and reimplement all the data
            for index, page_data in enumerate(all_pages_data["pages"]):
                # Ensure there's a specific page for this index
                self.switch_or_add_page(index, restore = True)
                print(index)
                # Access the newly added or existing page
                page = self.pages[index]
                page.image_path = page_data.get("image_path", "")
                page.set_background(page.image_path)

                #restore widgets on a page
                for widget_data in page_data.get("widgets", []):  #default to empty list if widgets key is missing
                    try:
                        widget_type = widget_data["type"]
                        if widget_type == "ButtonWidget":
                            position = QPoint(*widget_data["position"])
                            size_multiplier = tuple(widget_data["size_multiplier"])
                            functions = widget_data.get("functions")
                            color = widget_data.get("color")
                            label = widget_data.get("label")
                            image_path = widget_data.get("image_path")

                            #call pagegrid add_widget method to add widgets back to page
                            page.page_grid.add_widget(widget_type, size_multiplier, position, color, label, image_path)
                            # Optionally assign appID and style_sheet
                            last_widget = page.page_grid.widgets[-1]
                            last_widget.functions = functions
                        else:
                            print(f"Skipping type:{widget_type} is invalid")
                    except (KeyError, TypeError) as e:
                        print(f"Skipped restoring a widget due to invalid data: {widget_data}. Error: {e}")

        except Exception as e:
            print(f"Unexpected error while restoring pages: {e}")
        self.blockSignals(False)    #unblock signals after restoration
        self.update()   #update to ensure everything is loaded properly
