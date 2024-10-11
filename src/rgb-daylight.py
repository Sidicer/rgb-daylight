#!python3

from time import sleep
from rgb import RGB
from daylight import Daylight
from config import Config
import argparse
import sys

parser = argparse.ArgumentParser(description="Daylight simulator launch options")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
parser.add_argument("-d", "--debug", action="store_true",  help="Rapidly cycle colors")
parser.add_argument("-c", "--color-test", action="store",  help="Set to a specific daytime color")
args = parser.parse_args()

# Init configuration, rgb and daylight classes
config = Config("settings.json")
lights = RGB(config)
day = Daylight(config, lights)
# How often should the script be updated
delay = 1

if args.verbose:
    day.verbose = True

# Additional sets for debug
if args.debug:
    day.debug = True
    delay = 0.005

if args.color_test is not None:
    day.set_color(args.color_test)
    sys.exit()

try:
    # Update Daylight Controller
    while True:
        day.update()
        sleep(delay)
except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
finally:
    # Ensure cleanup of NeoPixel resources
    if hasattr(lights, "pixels") and lights.pixels is not None:
        lights.pixels.fill((0, 0, 0))
        lights.pixels.show()
        lights.pixels.deinit()
    print("Cleaned up NeoPixel resources.")