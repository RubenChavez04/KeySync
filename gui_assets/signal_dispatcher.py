from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QPushButton


class SignalDispatcher(QObject):
    #top bar signals
    add_widget_signal = pyqtSignal()
    change_page_background_signal = pyqtSignal() #background button clicked signal
    image_selected_signal = pyqtSignal(str) #image path signal
    page_full_signal = pyqtSignal(bool)
    save_pages_signal = pyqtSignal()

    #button customization signals used for
    icon_file_signal = pyqtSignal(str)
    update_position = pyqtSignal(QPushButton)
    function_press = pyqtSignal(str, int)
    remove_widget_signal = pyqtSignal(QPushButton)

    #appearance widget signals
    add_label_signal = pyqtSignal()
    delete_button_signal = pyqtSignal()
    add_icon_signal = pyqtSignal()
    change_color_signal = pyqtSignal()
    selected_button = pyqtSignal(QPushButton)

    #page delete signal
    tab_deleted_signal = pyqtSignal()

    #close signal
    close_app_signal = pyqtSignal()

    #server/client signals
    websocket_send_message = pyqtSignal(str)
    websocket_send_pages = pyqtSignal()

    #spotify widget global signals
    websocket_send_spot = pyqtSignal()
    websocket_send_spot_progress = pyqtSignal(str)
    start_spotify_tasker = pyqtSignal()
    stop_spotify_tasker = pyqtSignal()

    #weather widget global signals
    websocket_send_weather = pyqtSignal()

    #raspi button signal
    handle_function_signal = pyqtSignal(str)


#create a global dispatcher instance for calling in other py files
global_signal_dispatcher = SignalDispatcher()
