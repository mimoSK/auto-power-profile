# Auto Power Profile

An automatic power profile switcher designed for **Ubuntu 24**. This program dynamically adjusts the system's power profile based on CPU usage, system activity, when the device is connected to AC power. It ensures optimal performance during demanding tasks while conserving power during idle or low-usage periods.

## Features
- Automatically switches between `performance` and `balanced` power profiles.
- Monitors system activity, including:
  - CPU usage exceeding a configurable threshold.
  - Active monitored processes (e.g., compilers like `gcc`, `clang`, etc.).
- Detects AC power connection to ensure power profiles are adjusted only when plugged in.
- Configurable thresholds and timeouts for customization.
- Lightweight implementation using Python and Shell scripts.
- Efficiently integrates with `powerprofilesctl` and `systemd`.

---

## Installation

### Prerequisites
Ensure the following dependencies are installed before proceeding:
- **Python 3**
- **powerprofilesctl** (part of the `power-profiles-daemon` package)

### Steps to Install
1. Clone the repository and navigate to its directory:
   ```bash
   git clone https://github.com/mimoSK/auto-power-profile.git
   cd auto-power-profile
   ```

2. Run the `install.sh` script with root privileges:
   ```bash
   sudo ./install.sh
   ```

   The script performs the following:
   - Copies the `auto-power-profile.py` script to `/usr/local/bin`.
   - Installs the `auto-power-profile.service` file to `/etc/systemd/system/`.
   - Reloads the `systemd` daemon.
   - Enables and starts the `auto-power-profile` service.

3. Verify the installation:
   ```bash
   sudo systemctl status auto-power-profile.service
   ```

   If the service is running, the installation was successful.

---

## Configuration

The script comes with default thresholds and settings, but you can customize them by editing the `auto-power-profile.py` file:

- **CPU_THRESHOLD**: CPU usage threshold to switch to `performance` mode (default: 80%).
- **INACTIVITY_TIMEOUT**: Time (in seconds) to revert to `balanced` mode after high activity stops (default: 60 seconds).
- **MONITORED_PROCESS**: Semicolon-separated list of process names to monitor (default: `cc1plus;gcc;g++;clang;clang++`).
- **CHECK_INTERVAL**: Time interval (in seconds) between system checks (default: 5 seconds).

After making changes, restart the service:
```bash
sudo systemctl restart auto-power-profile.service
```

---

## Usage

Once installed, the service will automatically:
- Monitor CPU usage and specific processes.
- Switch power profiles between `performance` and `balanced` based on activity.

To view logs for troubleshooting:
```bash
journalctl -u auto-power-profile.service
```

---

## Contributing
Contributions are welcome! Please fork the repository, create a new branch for your feature or bug fix, and submit a pull request.

---

## License
This project is licensed under the GPL3 License. See the [LICENSE](./LICENSE) file for details.

## Support
If you encounter issues, feel free to open an [issue](https://github.com/mimoSK/auto-power-profile/issues) on GitHub.
