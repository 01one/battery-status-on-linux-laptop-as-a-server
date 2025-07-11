# Battery Status Monitor & Auto Shutdown

This project is a web-based battery monitor and automatic shutdown tool for Linux systems. It uses Tornado (Python web framework) to provide a simple web interface and background monitoring of battery status, with automatic shutdown scheduling when the battery is low.

## Features

- **Web Interface:**
  - View current battery status via a web page (`index.html`).
  - REST endpoint at `/status` returns raw battery info.
- **Automatic Shutdown:**
  - Monitors battery percentage and state every 5 minutes.
  - If battery drops to 20% or below and is discharging, schedules a system shutdown in 2 hours.
  - Cancels scheduled shutdown if battery condition improves.
- **Logging:**
  - Logs all actions and battery status to `battery_shutdown.log`.

## Requirements

- Linux system with `upower` and `shutdown` utilities available.
- Python 3.7+
- Tornado web framework

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/01one/battery-status-on-linux-laptop-as-a-server.git
   cd battery-status-on-linux-laptop-as-a-server
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the server:**
   ```bash
   sudo python3 app.py
   ```
   > **Note:** `sudo` is required for shutdown commands.

2. **Access the web interface:**
   - Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

3. **API Endpoint:**
   - Battery status: [http://127.0.0.1:5000/status](http://127.0.0.1:5000/status)

## How It Works

- The server checks battery status every 5 minutes using `upower`.
- If battery is low and discharging, it schedules a shutdown in 2 hours using `shutdown -h +120`.
- If battery condition improves, it cancels the scheduled shutdown using `shutdown -c`.
- All actions are logged in `battery_shutdown.log`.

## Security & Deployment
- The app requires `sudo` privileges to execute shutdown commands. Consider configuring `sudoers` to allow passwordless shutdown for the user running this script.
- For remote access, you can optionally set up a Cloudflare Tunnel and configure a custom domain. You may also use Nginx as a reverse proxy for added security and flexibility.

## License

MIT License

---

**Screenshot:**

![Screenshot](Screenshot%202025-07-11%20at%2014-04-46%20Battery%20Status%20Monitor.png)
