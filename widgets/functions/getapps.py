import os
import subprocess

def get_apps():
    # Get the directory of the current Python script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the relative path to your .ps1 script inside the project
    ps1_file_path = os.path.join(script_dir, "scripts", "getapps_ps1.ps1")  # Example: /scripts/example.ps1

    # Run the PowerShell script
    result = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps1_file_path],
                            capture_output=True, text=True)

    # Handle the result
    if result.returncode == 0:
        print("PowerShell script executed successfully!")
        print(result.stdout)
    else:
        print(f"Error running script: {result.stderr}")


if __name__ == "__main__":
    get_apps()
