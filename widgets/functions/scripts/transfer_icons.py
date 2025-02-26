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

def send_icons(folder_path):
    all_paths = get_icons(folder_path)
    for path in range(len(all_paths)):
        scp_command = f'scp "{all_paths[path]}" rubchave@10.0.6.151:/home/rubchave/gui_icons/'
        print(scp_command)
        output = subprocess.run(f'{scp_command} & 7477', shell=True, capture_output = True, text=True)
        print(output.stdout)
        #output = subprocess.run(f'{scp_command} & 7477', capture_output=True, text=True)
        #print("STDOUT:", output.stdout)
        #print("STDERR:", output.stderr)


send_icons(r'C:\Users\chave\PycharmProjects\PythonProject1\gui_assets\gui_icons')