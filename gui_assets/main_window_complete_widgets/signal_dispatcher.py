from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QPushButton


class SignalDispatcher(QObject):
    #top bar signals
    add_widget_signal = pyqtSignal()
    change_page_background_signal = pyqtSignal() #background button clicked signal
    image_selected_signal = pyqtSignal(str) #image path signal
    page_full_signal = pyqtSignal(bool)

    selected_button = pyqtSignal(QPushButton)

#create a global dispatcher instance for calling in other py files
global_signal_dispatcher = SignalDispatcher()
