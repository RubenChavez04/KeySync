from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedLayout

from pi_code.page_pi import Page  # Ensure the client-facing Page is imported
from pi_code.signal_dispatcher_pi import pi_signal_dispatcher
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(800, 480)  #set to screen size for the Pi
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        #central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        #stacked Layout for pages
        self.page_container = QStackedLayout()
        self.page_container.setContentsMargins(0, 0, 0, 0)
        self.pages = []  #list for pages
        central_layout.addLayout(self.page_container)
        self.restore_all_pages()
        pi_signal_dispatcher.change_page_signal.connect(lambda page_name: self.switch_or_add_page(page_name=page_name))
        pi_signal_dispatcher.update_pages.connect(self.new_save)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.BlankCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)

    def add_new_page(self):
        page = Page(self)  #create a new Page
        self.pages.append(page)
        self.page_container.addWidget(page)

    def switch_or_add_page(self,index=None, page_name=None, restore=False):
        """When a tab is changed or added, switch to page that is indexed with tab, else add a new page"""
        print("in change page")
        print(page_name)
        if not restore:
            self.blockSignals(False)
        if restore:
            self.blockSignals(True)
        if page_name is not None:
            for i, page in enumerate(self.pages):
                name = page.name
                print(f"printingname: {name}")
                if name == page_name:
                    index = i  # go to page indexed with tab
        if index is not None:
            if index >= len(self.pages):  # check if page exists with current amount of tabs
                self.add_new_page()  # add a new page
                print(index)
            self.page_container.setCurrentWidget(self.pages[index])

    def restore_all_pages(self, filepath="pi_assets/saved_pages.json"):
        """restore the pages on client launch, soon whenever a new json file is sent"""
        try:
            with open(filepath, "r") as file:
                all_pages_data = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading file {filepath}: {e}")
            return

        #validate the JSON files data
        if not all_pages_data.get("pages"):
            print(f"Error: Missing 'pages' key in {filepath}")
            return
        try:
            #get all data and reimplement all the data
            for index, page_data in enumerate(all_pages_data["pages"]):
                # Ensure there's a specific page for this index
                self.switch_or_add_page(index=index, restore = True)
                print(index)
                # Access the newly added or existing page
                page = self.pages[index]
                page.color = page_data.get("color", "#000000")
                page.name = page_data.get("name", f"Page {index+1}")
                page.set_background(page.color)
                #restore widgets on a page
                for widget_data in page_data.get("widgets", []):  #default to empty list if widgets key is missing
                    try:
                        widget_type = widget_data["type"]
                        position = QPoint(*widget_data["position"])
                        size_multiplier = tuple(widget_data["size_multiplier"])
                        color = widget_data.get("color")
                        functions = widget_data.get("functions")
                        label = widget_data.get("label")
                        image_path = widget_data.get("image_path")
                        #call pagegrid add_widget method to add widgets back to page
                        page.page_grid.add_widget(widget_type, size_multiplier, position, color, label, image_path)
                        last_widget = page.page_grid.widgets[-1]
                        last_widget.functions = functions
                    except (KeyError, TypeError) as e:
                        print(f"Skipped restoring a widget due to invalid data: {widget_data}. Error: {e}")
        except Exception as e:
            print(f"Unexpected error while restoring pages: {e}")
        self.switch_or_add_page(index = 0)
        self.blockSignals(False)    #unblock signals after restoration
        self.update()   #update to ensure everything is loaded properly

    def new_save(self):
        for page in self.pages:
            self.page_container.removeWidget(page)
            page.delete_page()
        self.pages.clear()
        self.restore_all_pages()
        print("Updated pages")