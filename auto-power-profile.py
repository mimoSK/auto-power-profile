#!/usr/bin/env python3
import psutil
import time
import subprocess
import logging
import systemd.daemon
import sys
from logging.handlers import SysLogHandler

# Configuration
CPU_THRESHOLD = 80  # CPU utilization threshold (%)
INACTIVITY_TIMEOUT = 60  # Seconds to wait before switching back to balanced
MONITORED_PROCESS = "cc1plus;gcc;g++;clang;clang++"  # Semicolon-separated monitored process names
CHECK_INTERVAL = 5  # Seconds between checks

# Set up logging to systemd journal
logger = logging.getLogger("AutoPowerProfile")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(name)s: %(levelname)s %(message)s")

handler = SysLogHandler(address="/dev/log")
handler.setFormatter(formatter)
logger.addHandler(handler)

# consoleHandler = logging.StreamHandler(sys.stdout)
# consoleHandler.setFormatter(formatter)
# logger.addHandler(consoleHandler)

def is_ac_power():
    """Check if the laptop is on AC power."""
    try:
        battery = psutil.sensors_battery()
        return battery is None or battery.power_plugged
    except Exception as e:
        logger.error(f"Failed to check AC power status: {e}")
        return False

def are_processes_running(process_names):
    """Check if any of the specified processes are running."""
    try:
        process_list = process_names.split(";")
        for proc in psutil.process_iter(["name"]):
            for process_name in process_list:
                if proc.info["name"].lower() == process_name.lower():
                    return True
        return False
    except Exception as e:
        logger.error(f"Failed to check for processes {process_names}: {e}")
        return False


def get_cpu_usage():
    """Get current CPU usage percentage."""
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        logger.error(f"Failed to get CPU usage: {e}")
        return 0

def set_power_profile(profile):
    """Set the power profile using powerprofilesctl."""
    try:
        result = subprocess.run(
            ["powerprofilesctl", "set", profile],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Switched to {profile} power profile")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set power profile to {profile}: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("powerprofilesctl not found. Is power-profiles-daemon installed?")
        return False

def main():
    """Main loop to monitor CPU and manage power profiles."""
    logger.info("Starting Auto power profile service")
    systemd.daemon.notify("READY=1")
    
    last_high_usage_time = None
    current_profile = "balanced"
    
    while True:
        try:
            # Check if on AC power
            if not is_ac_power():
                time.sleep(CHECK_INTERVAL)
                continue

            # Check CPU usage and monitored process
            cpu_usage = get_cpu_usage()
            processes_running = are_processes_running(MONITORED_PROCESS)

            # High CPU usage and monitored processes running
            if cpu_usage > CPU_THRESHOLD and processes_running:
                if current_profile != "performance":
                    if set_power_profile("performance"):
                        current_profile = "performance"
                last_high_usage_time = time.time()
            else:
                # Check for inactivity timeout
                if last_high_usage_time is not None:
                    elapsed = time.time() - last_high_usage_time
                    if elapsed >= INACTIVITY_TIMEOUT and current_profile != "balanced":
                        if set_power_profile("balanced"):
                            current_profile = "balanced"
                            last_high_usage_time = None

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Service stopped")
        systemd.daemon.notify("STOPPING=1")