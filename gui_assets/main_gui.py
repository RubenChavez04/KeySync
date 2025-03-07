from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QGridLayout,
    QStackedLayout
)

from gui_assets.buttons_sliders_etc.page import Page
from gui_assets.buttons_sliders_etc.shadow_fx import ShadowFX
from gui_assets.buttons_sliders_etc.title_bar import TitleBar
from gui_assets.main_window_complete_widgets.side_bar import SideBar
from gui_assets.main_window_complete_widgets.signal_dispatcher import global_signal_dispatcher
from gui_assets.main_window_complete_widgets.top_bar import TopBar
from gui_assets.popups.page_background_selection import ChangePageBackgroundDialog
from gui_assets.widgets import appearance_widget



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
        side_bar = SideBar(self)  #declare sidebar
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
        self.top_bar.tab_bar.tab_changed.connect(self.switch_or_add_page) #go to switch or add page when state change
        self.add_new_page() #add a default page

        #show popup to add widgets
        global_signal_dispatcher.add_widget_signal.connect(self.show_add_widget_popup)

        #show popup to change page background
        global_signal_dispatcher.change_page_background_signal.connect(self.show_background_dialog)
        global_signal_dispatcher.image_selected_signal.connect(self.update_page_background)

        #set the layout for the central widget
        title_bar_layout.addLayout(main_window_layout)
        main_window.setLayout(title_bar_layout)
        self.setCentralWidget(main_window)

    def add_new_page(self):
        """Add a new page to the page container when called"""
        page_shadow = ShadowFX(self, self.color) #decalre shadow fx
        page= Page(self) #set page to page class
        page.setGraphicsEffect(page_shadow) #add shadow fx
        self.pages.append(page) #add page to list
        self.page_container.addWidget(page) #add page to page container

    def switch_or_add_page(self,index):
        """When a tab is changed or added, switch to page that is indexed with tab, else add a new page"""
        if index >= len(self.pages): #check if page exists with current amount of tabs
            self.add_new_page() #add a new page
        self.page_container.setCurrentWidget(self.pages[index]) #go to page indexed with tab

    def show_add_widget_popup(self):
        #get the current page from index and show popup for respective page
        current_page = self.pages[self.page_container.currentIndex()]
        current_page.show_add_widget_popup()

    def show_background_dialog(self):
        """Open the image import dialog."""
        dialog = ChangePageBackgroundDialog()
        dialog.exec()

    def update_page_background(self, image_path):
        """Update the background of the current page."""
        current_page = self.pages[self.page_container.currentIndex()]
        current_page.update_background(image_path)
