#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
from config.config import SCRIPT_PATH


def setup_scheduler():
    if not SCRIPT_PATH:
        raise ValueError("SCRIPT_PATH not found in environment variables")

    # Get the absolute path of the script directory
    script_dir = Path(__file__).parent.absolute()

    # Create logs directory if it doesn't exist
    logs_dir = script_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Define paths
    plist_source = script_dir / "com.yourapp.scheduler.plist"
    plist_dest = Path.home() / "Library/LaunchAgents/com.yourapp.scheduler.plist"

    # Read the plist template
    with open(plist_source, "r") as f:
        plist_content = f.read()

    # Replace the placeholders
    plist_content = plist_content.replace("YOUR_SCRIPT_PATH_HERE", SCRIPT_PATH)
    plist_content = plist_content.replace("YOUR_PROJECT_PATH_HERE", str(script_dir))

    # Create LaunchAgents directory if it doesn't exist
    os.makedirs(Path.home() / "Library/LaunchAgents", exist_ok=True)

    # Write the modified plist file
    with open(plist_dest, "w") as f:
        f.write(plist_content)

    # Set correct permissions
    os.chmod(plist_dest, 0o644)

    # Load the launchd job
    try:
        subprocess.run(["launchctl", "unload", str(plist_dest)], check=False)
        subprocess.run(["launchctl", "load", str(plist_dest)], check=True)
        print("Successfully installed and loaded the scheduler!")
        print(f"The script will run at startup and every 3 hours from 9 AM to 9 PM")
        print(f"Logs will be written to: {logs_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error loading the launchd job: {e}")


if __name__ == "__main__":
    setup_scheduler()
