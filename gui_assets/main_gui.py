from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QGridLayout,
    QStackedLayout, QMenu, QSystemTrayIcon, QColorDialog
)

from gui_assets.buttons_sliders_etc.page import Page
from gui_assets.buttons_sliders_etc.shadow_fx import ShadowFX
from gui_assets.buttons_sliders_etc.title_bar import TitleBar
from gui_assets.main_window_complete_widgets.side_bar import SideBar
from gui_assets.signal_dispatcher import global_signal_dispatcher
from gui_assets.main_window_complete_widgets.top_bar import TopBar
from gui_assets.popups.page_background_selection import ChangePageBackgroundDialog
from server import shutdown_server
from widgets.functions.launch_close_app import exec_button_press
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #give our window a title
        self.setWindowTitle("KeySync")
        self.setContentsMargins(10,10,10,10)
        #set the window size
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.color = QColor(0, 0, 0, 150)
        self.shadow = ShadowFX(self, self.color)

        #System Tray stuff, used when you "close" the application,
        # system tray is where user can actually end application
        self.is_hidden_to_tray = False
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(
            "gui_assets/gui_icons/trash.ico"
        ))
        self.tray_icon.setToolTip("KeySync")
        #Tray menu
        self.tray_menu = QMenu()
        #Tray menu restore
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.restore_from_tray)
        self.tray_menu.addAction(restore_action)
        #tray menu quit app
        quit_action = QAction("Quit",self)
        quit_action.triggered.connect(self.close_app)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        side_bar_shadow = ShadowFX(self, self.color)
        top_bar_shadow = ShadowFX(self, self.color)

        #central widget for the main window
        main_window = QWidget(self)
        main_window.setFixedSize(1265, 630)
        main_window.setGraphicsEffect(self.shadow)
        main_window.setObjectName("Container")
        main_window.setStyleSheet(
            """#Container {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #171717,
                    stop: 1 #2b2d30
                );
                border-radius: 8px;
            }"""
        )
        #layout for the central widget
        main_window_layout = QGridLayout()
        #set margins to zero since spacer items allow for better shadowing
        main_window_layout.setContentsMargins(10, 10, 10, 10)
        #set spacing between items
        main_window_layout.setVerticalSpacing(5)
        main_window_layout.setHorizontalSpacing(5)

        #add custom title bar
        title_bar = TitleBar(self)
        title_bar_layout = QVBoxLayout() #title bar get its own layout so it spans window properly
        title_bar_layout.setContentsMargins(0,0,0,0) #set no margins for items to be close to top corners
        title_bar_layout.setSpacing(0) #no spacing, just one object
        title_bar_layout.addWidget(title_bar) #add title bar to layout

        #sidebar widget (Add this on the left of the frame)
        side_bar = SideBar(parent=self)  #declare sidebar
        side_bar.setGraphicsEffect(side_bar_shadow) #add sidebar shadow
        main_window_layout.setColumnStretch(0, 1)  #set a column stretch so that the sidebar fits
        main_window_layout.addWidget(side_bar, 0, 0, 2, 1)  #add sidebar to layout

        #page container for adding multiple pages
        self.page_container = QStackedLayout()  #create a stacked layout which can be indexed
        self.page_container.setContentsMargins(0, 0, 0, 0) #no margins so page fits fully
        self.pages = [] #a list for pages to be inserted
        main_window_layout.addLayout(self.page_container, 1, 1, alignment=Qt.AlignmentFlag.AlignTop) #add page container to layout

        #topbar for frame editing
        self.top_bar = TopBar(self) #call TopBar class
        self.top_bar.setGraphicsEffect(top_bar_shadow)
        main_window_layout.setRowStretch(0,1)
        main_window_layout.addWidget(self.top_bar, 0, 1, alignment=Qt.AlignmentFlag.AlignTop) #add top bar to layout

        #connect the tabs of the current page
        self.top_bar.tab_bar.tab_changed.connect(lambda index: self.switch_or_add_page(index=index)) #go to switch or add page when state change

        #run button function
        global_signal_dispatcher.function_press.connect(exec_button_press)

        #show popup to add widgets
        global_signal_dispatcher.add_widget_signal.connect(self.show_add_widget_popup)

        #show popup to change page background
        global_signal_dispatcher.change_page_background_signal.connect(self.show_background_dialog)
        global_signal_dispatcher.image_selected_signal.connect(self.update_page_background)
        global_signal_dispatcher.close_app_signal.connect(self.close_event)
        global_signal_dispatcher.tab_deleted_signal.connect(self.handle_tab_deletion)
        global_signal_dispatcher.save_pages_signal.connect(self.save_all_pages_data)
        global_signal_dispatcher.tab_renamed_signal.connect(self.update_page_name)
        global_signal_dispatcher.change_page_signal.connect(lambda page: self.switch_or_add_page(page_name=page))

        #set the layout for the central widget
        title_bar_layout.addLayout(main_window_layout)
        main_window.setLayout(title_bar_layout)
        self.setCentralWidget(main_window)
        print(f"SideBar Parent: {type(side_bar.parent)}")  # Should print: <class 'main_gui.MainWindow'>

    def init(self, bypass=False):
        file_path = "pi_assets/saved_pages.json"
        if not bypass:
            if os.path.exists(file_path):
                print(f"{file_path} exists")
                self.restore_all_pages()
                return
            else:
                self.add_new_page()
        if bypass:
            self.add_new_page()

    def close_event(self):
        """
        This method is called when the user tries to close the window.
        Instead of closing, we'll minimize the app to the system tray.
        """
        # Minimize to the system tray instead of quitting
        if not self.is_hidden_to_tray:
            self.hide()  # Hide the main application window
            self.tray_icon.showMessage(
                "KeySync is running",
                "The app is still running in the background. Click the tray icon to restore it.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            self.is_hidden_to_tray = True

    def on_tray_icon_activated(self, reason):
        """
        Handle clicks on the system tray icon.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single left click: Restore the app
            if self.isHidden():
                self.restore_from_tray()

    def restore_from_tray(self):
        self.is_hidden_to_tray = False
        self.showNormal()
        self.activateWindow()

    def close_app(self):
        self.tray_icon.hide()
        self.save_all_pages_data(close=True)
        self.window().close()
        shutdown_server()

    def add_new_page(self):
        """Add a new page to the page container when called"""
        page_shadow = ShadowFX(self, self.color) #decalre shadow fx
        page= Page(self) #set page to page class
        page.setGraphicsEffect(page_shadow) #add shadow fx
        self.pages.append(page) #add page to list
        self.page_container.addWidget(page) #add page to page container
        page.name = f"Page {len(self.pages)}"

    def switch_or_add_page(self,index = None, page_name = None, restore=False):
        """When a tab is changed or added, switch to page that is indexed with tab, else add a new page"""
        if not restore:
            self.blockSignals(False)
        if restore:
            self.blockSignals(True)
        if page_name is not None:
            for i, page in enumerate(self.pages):
                name = self.pages[i].name
                if name == page_name:
                    self.page_container.setCurrentWidget(self.pages[i]) #go to page indexed with tab
                    self.top_bar.tab_bar.change_tab(i)
                    return
        elif index is not None:
            if index >= len(self.pages):  # check if page exists with current amount of tabs
                self.add_new_page()  # add a new page
            self.page_container.setCurrentWidget(self.pages[index])
            return

    def update_page_name(self, new_name, index):
        if index < len(self.pages):
            self.pages[index].name = new_name
            print(f"Name:{new_name} Index:{index}")

    def handle_tab_deletion(self, index):
        current_widget = self.page_container.currentWidget()
        if index <= len(self.pages):  # Ensure the index is valid
            page_to_remove = self.pages.pop(index)  # Remove the page from the list
            self.page_container.removeWidget(page_to_remove)  # Remove it from the stacked layout
            page_to_remove.delete_page()  # Clean up the widget

        if not self.pages:
            self.add_new_page()
            new_index = 0
        else:
            if current_widget in self.pages:
                new_index = self.page_container.currentIndex()
            else:
                new_index = 0
        self.switch_or_add_page(index=new_index)
        self.top_bar.tab_bar.change_tab(new_index)

    def show_add_widget_popup(self):
        #get the current page from index and show popup for respective page
        current_page = self.pages[self.page_container.currentIndex()]
        current_page.show_add_widget_popup()

    def show_background_dialog(self):
        """Open the image import dialog."""
        color = QColorDialog.getColor(initial=QColor(255, 255, 255), title="Select Color")
        if color.isValid():
            color = color.name()
            self.update_page_background(color)

    def update_page_background(self, color):
        """Update the background of the current page."""
        current_page = self.pages[self.page_container.currentIndex()]
        current_page.set_background(color)

    def save_all_pages_data(self,close=False):
        page_save_path = "pi_assets/saved_pages.json"
        all_pages_data = {
            "pages":[]
        }

        for page in self.pages:
            page_data = page.save_page_data()
            all_pages_data["pages"].append(page_data)

        try:
            with open(page_save_path, "w") as save_file:
                json.dump(all_pages_data, save_file, indent=4)
            print(f"All page data saved to {page_save_path}")
        except IOError as e:
            print(f"Error saving page data{e}")
        if not close:
            global_signal_dispatcher.websocket_send_pages.emit()

    def restore_all_pages(self, filepath="pi_assets/saved_pages.json"):
        try:
            with open(filepath, "r") as file:
                all_pages_data = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading file {filepath}: {e}")
            self.init(bypass=True)  # If file doesn't exist, initialize a new page
            return

        # Validate the JSON data
        if not all_pages_data.get("pages"):
            print(f"Error: Missing 'pages' key in {filepath}")
            self.init(bypass=True)  # If 'pages' key is missing, initialize a new page
            return

        try:
            # Loop through all pages in JSON
            for index, page_data in enumerate(all_pages_data["pages"]):
                # Ensure the page exists in the stack layout
                self.switch_or_add_page(index=index, restore=True)

                # Access the newly added page
                page = self.pages[index]

                # Restore the page's background
                page.color = page_data.get("color", "#000000")
                #page.image_path = page_data.get("image_path", "")
                page.name = page_data.get("name", f"Page {index+1}")
                page.set_background(page.color)

                # Only add a new tab for restored pages
                if index == 0:
                    self.top_bar.tab_bar.tab_buttons[0].setText(page.name)
                if len(self.top_bar.tab_bar.tab_buttons) <= index:
                    print(f"index:{index} name:{page.name}")
                    self.top_bar.tab_bar.add_new_tab()
                    self.top_bar.tab_bar.tab_buttons[-1].setText(page.name)

                # Restore widgets on the page
                for widget_data in page_data.get("widgets", []):
                    try:
                        widget_type = widget_data["type"]
                        position = QPoint(*widget_data["position"])
                        size_multiplier = tuple(widget_data["size_multiplier"])
                        functions = widget_data.get("functions")
                        color = widget_data.get("color")
                        label = widget_data.get("label")
                        image_path = widget_data.get("image_path")

                        # Call `page_grid.add_widget` to restore widgets
                        page.page_grid.add_widget(widget_type, size_multiplier, position, color, label, image_path)
                        # Assign additional properties (if any)
                        last_widget = page.page_grid.widgets[-1]
                        last_widget.functions = functions
                    except (KeyError, TypeError) as e:
                        print(f"Error restoring widget data: {widget_data}. Error: {e}")

        except Exception as e:
            print(f"Unexpected error while restoring pages: {e}")

        # Unblock signals after restoration and reset to the first tab
        self.blockSignals(False)
        self.top_bar.tab_bar.change_tab(0)
        self.update()  # Ensure everything is rendered correctly
        print("Finished restoring all pages")





