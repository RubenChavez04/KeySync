import os
import subprocess

def get_icons(folder_path):
    all_paths = []
    for filename in os.listdir(folder_path): #For file in folder
        filepath = os.path.join(folder_path, filename) #joins C:/.../ and filename together
        if os.path.isfile(filepath): #Makes sure it's a file and not a folder
            all_paths.append(filepath) #Adds filepath to the paths array
        else:
            pass
    return all_paths

