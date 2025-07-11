import tornado.ioloop
import tornado.web
import subprocess
import re
import logging
from datetime import datetime
import asyncio

logging.basicConfig(
    filename="battery_shutdown.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SHUTDOWN_SCHEDULED = False

def get_battery_info_blocking():
    try:
        devices = subprocess.check_output(["upower", "-e"]).decode().splitlines()
        battery_device = next((d for d in devices if 'battery' in d), None)
        if not battery_device:
            logging.warning("No battery device found.")
            return None
        status_output = subprocess.check_output(["upower", "-i", battery_device]).decode()
        return status_output
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching battery info: {e}")
        return None

def parse_battery_status(status_output):
    percentage_match = re.search(r'percentage:\s+(\d+)%', status_output)
    state_match = re.search(r'state:\s+(\w+)', status_output)
    if percentage_match and state_match:
        return int(percentage_match.group(1)), state_match.group(1)
    logging.error("Failed to parse battery status.")
    return None, None

def run_shutdown_command_blocking(args):
    subprocess.call(["sudo", "/sbin/shutdown"] + args)

async def check_battery_and_maybe_shutdown():
    global SHUTDOWN_SCHEDULED

    status = await asyncio.to_thread(get_battery_info_blocking)
    if not status:
        return

    percent, state = parse_battery_status(status)
    logging.info(f"Battery at {percent}%, state: {state}")

    if percent is None or state is None:
        return

    if percent <= 20 and state == "discharging":
        if not SHUTDOWN_SCHEDULED:
            logging.warning("Battery low and discharging. Scheduling shutdown in 2 hours.")
            await asyncio.to_thread(run_shutdown_command_blocking, ["-h", "+120"])
            SHUTDOWN_SCHEDULED = True
        else:
            logging.debug("Shutdown already scheduled.")
    else:
        if SHUTDOWN_SCHEDULED:
            logging.info("Battery condition improved. Cancelling scheduled shutdown.")
            await asyncio.to_thread(run_shutdown_command_blocking, ["-c"])
            SHUTDOWN_SCHEDULED = False

class StatusHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()

    async def get(self):
        status = await asyncio.to_thread(get_battery_info_blocking)
        self.write(status or "Unable to fetch battery status.")

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        return self.render('index.html')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/status", StatusHandler),
    ], debug=True)

if __name__ == "__main__":
    logging.info("Starting server for battery monitor...")
    app = make_app()
    app.listen(address="127.0.0.1", port=5000)

    # Tornado's async PeriodicCallback with awaitable coroutine
    async def periodic_wrapper():
        await check_battery_and_maybe_shutdown()

    tornado.ioloop.PeriodicCallback(periodic_wrapper, 5 * 60 * 1000).start()

    tornado.ioloop.IOLoop.current().start()
