import os
global appList
appList = [['Chrome', r'C:\Program Files\Google\Chrome\Application\chrome.exe']]

def getFilePath(appName):
    for i in appList:
        if appList[i][0] == appName:
            return appList[i][1]

def runButtonFunction(appName, desiredFunction):
    if desiredFunction == 'Open':
        filePath = getFilePath(appName)
        os.startfile(filePath)
    else:
        pass

runButtonFunction('Chrome', 'Open')

