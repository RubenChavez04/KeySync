from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.functions.button_functions import *
#from KeySync import entire_project
#entire_project.run()

"""
Example message:
Launch App:{app file path}

"""
def handle_message(message):
    colon_start = message.find(":")
    selected_function = message[0:colon_start]
    function_param = message[colon_start+1:]

    if "Launch" in selected_function:
        open_app(function_param)
    else:
        print("Function not recognized")
    return
