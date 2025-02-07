#this is the script we use
#set path to current directory of the shell script, that way the csv gets added into the cd of the script
$csvPath = "$PSScriptRoot\InstalledApps.csv"

#get the installed applications name and ID and export to a csv
#NOTE: the csv gets overridden everytime, which works in our favor
#we can also just add a refresh function to get all new installed apps if the program is running
Get-StartApps | Select-Object Name, AppID | Export-Csv -Path $csvPath -NoTypeInformation

#We can run this script in python using os.system("put script here")