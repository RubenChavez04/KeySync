from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.functions.launch_close_app import *

#from KeySync import entire_project
#entire_project.run()
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
"""
Example message:
Launch App:{app file path}

"""
global_signal_dispatcher.handle_function_signal.connect(lambda function: handle_message(function))

def handle_message(message):
    colon_start = message.split(":")
    function = colon_start[0]
    if function == "Launch App":
        if colon_start[2] is not None:
            param = str(colon_start[1]+":"+colon_start[2])
        else:
            param = str(colon_start[1])
        print(param)
        if ".lnk" in param:
            os.startfile(param)
        else:
            open_app(param)
    elif function == "spotify":
        param = colon_start[1]
        global_signal_dispatcher.run_spot_func.emit(param)
    elif function == "Change Page":
        param = colon_start[1]
        global_signal_dispatcher.change_page_signal.emit(param)
    elif function == "Open URL":
        params = colon_start[1:]
        param = None
        for i,p in enumerate(params):
            param_temp = p
            if i == 1:
                param = param_temp
            else:
                if param is not None:
                    param = param+":"+param_temp
                else:
                    param = param_temp
        webbrowser.open(param)
    else:
        print("Function not recognized")
    return


