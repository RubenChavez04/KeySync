#Shell code to retrieve all apps from windows registry, since Start-Apps only returns application from the start menu
#We have to use registry since it also gets applications installed on other drives

$csvpath = "$PSScriptRoot\AllInstalledApps"

#default path to steamapps library to retrieve game ID to launch games
$steamLibraryDataPath = "$env:ProgramFiles(x86)\Steam\steamapps\libraryfolders.vdf"

#check if the path exists on users PC if not skip retrieving steam games and get other apps
if (Test-Path $steamLibraryDataPath) {
    Write-Output "Steam Library Path exists"
    #set an empty array for storing games found
    $steamgames = @()
    #get raw data from .vdf file
    $steamLibraryData = Get-Content -Path $steamLibraryDataPath -Raw
    #get library path
    $steamLibraryPaths = "$env:ProgramFiles(x86)\Steam\steamapps"
    #check for all other libraries in other drives or other install locations
    $matches = [regex]::Matches($steamLibraryData, '"path"\s*"([^"]+)"')
    #append the steam library paths if other paths exists and validate their location
    foreach ($match in $matches) {
        $librarypath = $match.Groups[1].Value #get the library path if match
        if (Test-Path $librarypath){    #validate path exists
            $steamLibraryPaths += "$librarypath\steamapps" #add path to paths
        }
    }
    foreach ($library in $steamLibraryPaths) {
        #get all the manifest file data from games to pull ID
        $manifestFiles = Get-ChildItem -path $library
    }
}

