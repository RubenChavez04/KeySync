import os
global appList
import subprocess
import psutil
global buttonFunctionList
global shellpid
import time

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

def runFunction(app,function):
    if function == 'Open':
        shell_process = subprocess.Popen(getFilePath(app), shell=True, close_fds=True)
        updateShellpid(app,shell_process.pid)
    elif function == 'Close':
        closeApp(app)

def closeApp(app):
    child_pid = getChildShell(app)
    if child_pid:
        subprocess.run(["taskkill", "/PID", str(child_pid), "/T", "/F"], shell=True)
    else:
        pid = getShellpid(app)
        if pid:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], shell=True)

def getFilePath(app): #App ID not file path, shell uses that, sometimes it is a filepath if there is no app id associated with it
    for i in range(len(appList)):
        if appList[i][0] == app:
            return appList[i][1]

def getAppName(buttonID):
    return buttonFunctionList[buttonID][0]

def getButtonFunction(buttonID,pressType):
    return buttonFunctionList[buttonID][pressType]

def execButtonPress(buttonID, pressType):
    app = getAppName(buttonID)
    function = getButtonFunction(buttonID, pressType+1)
    runFunction(app,function)


shellpid = [['Chrome',],['Spotify',]]
buttonFunctionList = [['Chrome', 'Open'], ['Spotify', 'Open', 'Close']]
appList = [ ['Chrome','C:/'], ['Spotify', r'C:/Program Files/WindowsApps/SpotifyAB.SpotifyMusic_1.230.1135.0_x64__zpdnekdrzrea0/Spotify.exe']]
#should open spotify

execButtonPress(1,0)
time.sleep(5)
execButtonPress(1,1)



