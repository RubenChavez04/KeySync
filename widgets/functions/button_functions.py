import os

#from gui_assets.buttons_sliders_etc.page import signal_dispatcher

global appList
import subprocess
import psutil
global buttonFunctionList
global shellpid
import time
import webbrowser

#from gui_assets.main_window_complete_widgets.signal_dispatcher import global_signal_dispatcher
#signal_dispatcher = global_signal_dispatcher

shellpid = [['Chrome',],['Spotify',]]
buttonFunctionList = [['Chrome', 'Open', 'Close'], ['Spotify', 'Open', 'Close']]
appList = [ ['Chrome','https://www.youtube.com/feed/subscriptions'], ['Spotify', r'C:/Program Files/WindowsApps/SpotifyAB.SpotifyMusic_1.230.1135.0_x64__zpdnekdrzrea0/Spotify.exe']]

def updateButtonFunction(buttonID, function, pressType):
    buttonFunctionList[buttonID][pressType] = function

def updateAppList(newAppList):
    appList = newAppList

def assignAppName(buttonID,name):
    buttonFunctionList[buttonID][0] = name

def updateShellpid(app,pid):
    for i in range(len(shellpid)):
        if shellpid[i][0] == app:
            if len(shellpid[i]) == 1:
                shellpid[i].append(pid)
            else:
                shellpid[i][1] = pid

def getShellpid(app):
    for i in range(len(shellpid)):
        if shellpid[i][0] == app:
            return shellpid[i][1]

def getChildShell(app):
    parent = psutil.Process(getShellpid(app))
    children = parent.children(recursive=True)
    child_pid = children[0].pid
    return child_pid

def runFunction(app, function):
    filepath = getFilePath(app)
    if function == 'Open':
        if filepath.startswith("URL "):  # Given from getFilePath, will start with 'URL '
            webbrowser.open(filepath[4:])  # Start reading after 'URL ' to open the actual URL
        else:  # Else, it's either a normal exe or a microsoft app, run normally with the MSA path
            try:
                os.startfile(filepath)
            except Exception as e:
                print(f"Failed to start file using os.startfile: {e}")
                shell_process = subprocess.Popen([filepath], shell=True, close_fds=True)
                updateShellpid(app, shell_process.pid)
    elif function == 'Close':
        closeApp(app)

'''
def runFunction(app, function):
    filepath = getFilePath(app)
    if function == 'Open':
        if app == 'Chrome':
            webbrowser.open(filepath)
        else:
            shell_process = subprocess.Popen(filepath, shell=True, close_fds=True)
            updateShellpid(app, shell_process.pid)
    elif function == 'Close':
        closeApp(app)
'''
#def runFunction():
#    webbrowser.open('https://www.youtube.com/feed/subscriptions')

def closeApp(app):
    child_pid = getChildShell(app)
    if child_pid:
        subprocess.run(["taskkill", "/PID", str(child_pid), "/T", "/F"], shell=True)
    else:
        pid = getShellpid(app)
        if pid:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], shell=True)

def getFilePath(app):
    for i in range(len(appList)):
        if appList[i][0] == app:
            app_id = appList[i][1]
            if app_id.startswith("http"): #URL
                return f"URL {app_id}"
            elif "!" in app_id: #Only microsoft apps have  !in them
                return f"explorer.exe shell:appsFolder\\{app_id}"
            else: #Normal exe
                return app_id

def getAppName(buttonID):
    return buttonFunctionList[buttonID][0]

def getButtonFunction(buttonID,pressType):
    return buttonFunctionList[buttonID][pressType]

'''
def execButtonPress(buttonID, pressType):
    print('lol')
    app = getAppName(buttonID)
    function = getButtonFunction(buttonID, pressType)
    runFunction(app,function)
    print('Button Pressed')
'''

def execButtonPress(app_id, pressType):
    print(f'Executing button press for {app_id}')
    # Extract app name from app id assuming it follows Microsoft AppName_xyz!
    if '!' in app_id:
        app_name = app_id.split('!')[0].split('.')[-1].replace('_', ' ')
    else:
        app_name = app_id

    # Update button function list if app doesn't exist
    if not any(app_name in sublist for sublist in buttonFunctionList):
        buttonFunctionList.append([app_name, 'Open', 'Close'])
        shellpid.append([app_name])

    # Add to appList if not present
    if not any(app_name in sublist for sublist in appList):
        appList.append([app_name, app_id])

    function = 'Open' if pressType == 1 else 'Close'
    runFunction(app_name, function)
    print('Button Pressed')

#global_signal_dispatcher.function_press.connect(execButtonPress)
# After connecting the signal
#print("Signal connected:", global_signal_dispatcher.function_press.receivers() > 0)
#should open spotify

#execButtonPress(1,0)
#time.sleep(5)
#execButtonPress(1,1)



