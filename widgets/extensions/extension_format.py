from gui_assets.signal_dispatcher import global_signal_dispatcher

def your_function_name(params):
    1+1;
    return "Function stuff above, dont return"


#function gets sent in the format function_name:function_params
#can use multiple params using more colons and using the func_result index
def function_handler(function):
    func_result = function.split(":")
    function = func_result[0]
    param = func_result[1]
    try:
        if function == "your_function_name":
            #type what the function does here
            your_function_name(param)

    except Exception as e:
        print("Error running function: e")

global_signal_dispatcher.handle_function_signal.connect(lambda function: function_handler(function))