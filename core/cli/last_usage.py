from datetime import datetime
import os

USAGE_FILE = ".usage.dat"

def check_last_usage():
    """
    Checks the last usage time from USAGE_FILE and displays the logo if
    more than one minute has passed since the last execution.
    Updates the usage file with the current datetime.
    """
    current_time = datetime.now()
    display_logo = False

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            last_usage_str = f.read().strip()
        try:
            last_usage = datetime.fromisoformat(last_usage_str)
            if (current_time - last_usage).total_seconds() > 60:
                display_logo = True
        except ValueError:
            print("Error reading usage file; resetting timestamp.")

    else:
        display_logo = True

    with open(USAGE_FILE, "w") as f:
        f.write(current_time.isoformat())

    return display_logo