import os
import subprocess
import winreg
import glob
import time
import re


def get_windows_installed_apps():
    """Retrieve installed applications from Windows registry."""
    apps = {}

    registry_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hive, subkey in registry_keys:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(hive, subkey + "\\" + subkey_name) as subkey_handle:
                            app_name, _ = winreg.QueryValueEx(subkey_handle, "DisplayName")

                            install_path = None
                            try:
                                install_path, _ = winreg.QueryValueEx(subkey_handle, "InstallLocation")
                            except FileNotFoundError:
                                pass

                            if install_path and os.path.exists(install_path):
                                apps[app_name] = {"type": "regular", "path": install_path}
                    except (FileNotFoundError, OSError, TypeError):
                        continue
        except FileNotFoundError:
            continue
    return apps


def get_steam_library_paths():
    """Retrieve all Steam library paths from libraryfolders.vdf."""
    steam_path = os.path.join(os.environ["ProgramFiles(x86)"], "Steam")
    library_folders_file = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    library_paths = []

    if not os.path.exists(library_folders_file):
        return [os.path.join(steam_path, "steamapps")]

    try:
        with open(library_folders_file, "r", encoding="utf-8") as f:
            data = f.read()

        paths = re.findall(r'"path"\s+"([^"]+)"', data)
        for path in paths:
            library_paths.append(os.path.join(path, "steamapps"))

        library_paths.append(os.path.join(steam_path, "steamapps"))  # Add default Steam location

    except Exception as e:
        print(f"Error reading Steam library: {e}")

    return library_paths


def get_installed_steam_games():
    """Retrieve Steam game IDs and install paths from appmanifest files."""
    steam_games = {}

    for steamapps_path in get_steam_library_paths():
        for manifest in glob.glob(os.path.join(steamapps_path, "appmanifest_*.acf")):
            try:
                game_id = os.path.basename(manifest).replace("appmanifest_", "").replace(".acf", "")

                with open(manifest, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract the game's install directory from the ACF file
                match = re.search(r'"installdir"\s+"([^"]+)"', content)
                if match:
                    game_folder = match.group(1)
                    game_path = os.path.join(steamapps_path, "common", game_folder)
                    if os.path.exists(game_path):
                        steam_games[game_folder] = {
                            "type": "steam",
                            "id": game_id,
                            "steam_url": f"steam://rungameid/{game_id}",
                            "path": game_path
                        }
            except Exception as e:
                print(f"Error processing {manifest}: {e}")

    return steam_games


def find_executable(install_path):
    """Search for the main executable file in the game's folder."""
    if not install_path or not os.path.exists(install_path):
        return None

    exe_files = [file for file in glob.glob(os.path.join(install_path, "*.exe"))]

    if not exe_files:
        return None

    # Ignore known background processes
    ignore_keywords = ["unins", "setup", "helper", "update", "uninstall", "launcher", "network", "tools"]
    exe_files = [exe for exe in exe_files if not any(keyword in exe.lower() for keyword in ignore_keywords)]

    if not exe_files:
        return None

    exe_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
    best_exe = exe_files[0]

    print(f"Identified main executable: {best_exe}")

    return best_exe


def get_all_installed_apps():
    """Merge Windows installed apps and Steam games while removing duplicates."""
    windows_apps = get_windows_installed_apps()
    steam_games = get_installed_steam_games()

    # Merge both dictionaries while avoiding duplicates
    all_apps = {**windows_apps, **steam_games}

    return all_apps


def launch_app(app_name):
    """Launch an application, prioritizing Steam games."""
    installed_apps = get_all_installed_apps()

    if app_name not in installed_apps:
        print(f"Application '{app_name}' not found.")
        return

    app_info = installed_apps[app_name]

    if app_info["type"] == "steam":
        steam_id = app_info["id"]
        steam_url = app_info["steam_url"]
        game_path = app_info["path"]

        print(f"Launching {app_name} via Steam (App ID: {steam_id})")
        print(f"Steam URL: {steam_url}")
        print(f"Install Path: {game_path}")

        # Use explorer.exe to start the Steam URL properly
        try:
            subprocess.Popen(["explorer.exe", steam_url], shell=True)
            print(f"Successfully launched {app_name} via Steam!")
            return
        except Exception as e:
            print(f"Error launching {app_name} via Steam: {e}")

        # If Steam fails, try direct executable
        time.sleep(5)
        exe_path = find_executable(game_path)
        if exe_path:
            print(f"Steam launch failed, launching {app_name} directly from: {exe_path}...")
            subprocess.Popen(exe_path, shell=True)
        else:
            print(f"Could not locate the executable for {app_name}.")

    elif app_info["type"] == "regular":
        exe_path = find_executable(app_info["path"])
        if exe_path:
            print(f"Launching {app_name} from {exe_path}...")
            subprocess.Popen(exe_path, shell=True)
        else:
            print(f"Executable for '{app_name}' not found in {app_info['path']}.")


# Get the list of all installed apps
installed_apps = get_all_installed_apps()
for app, info in installed_apps.items():
    if info["type"] == "steam":
        print(f"{app} - Steam App ID: {info['id']} - Steam URL: {info['steam_url']} - Install Path: {info['path']}")
    else:
        print(f"{app} - Install Path: {info['path']}")

# Example: Launch any installed app
launch_app("")  # Works for normal apps
