from datetime import datetime, timezone, timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
import sys

class Daylight(object):

    def __init__(self, config, rgb):
        self.config = config
        self.lights = rgb
        self._position = None
        self.position = self.config.get("position", {"timezone": "America/Phoenix", "latitude": 33.434061, "longitude": -112.016303})
        self.timezone = pytz.timezone(self.position['timezone'])
        self._sun = None
        self.timezone_hours = self.config.get("timezone_offset", 0)
        self.colors_default = {
            "night-end": [0, 0, 0.05],
            "dawn": [0.1, 0.1, 0.3],
            "sunrise": [0.4, 0.4, 0.4],
            "noon": [1, 1, 1],
            "sunset": [0.5, 0.25, 0.1],
            "dusk": [0.3, 0.1, 0.4],
            "night-start": [0, 0, 0.05]
        }
        self.colors = self.config.get("colors", self.colors_default)
        self.times = ['night-end', "dawn", "sunrise", "noon", "sunset", "dusk", 'night-start']
        self.start = self.tz_fix(datetime.now())
        self.location = LocationInfo(self.position['timezone'], self.position['timezone'], self.position['latitude'], self.position['longitude'])
        self.test = False

    def set_color(self, color):
        self.lights.color = self.colors[color]

    def update(self):
        self._sun = self.sun  # Cache results of sun property
        s = self._sun

        sun_info = {
            'night-end': s['night-end'].astimezone(self.timezone),
            'dawn': s['dawn'].astimezone(self.timezone),
            'sunrise': s['sunrise'].astimezone(self.timezone),
            'noon': s['noon'].astimezone(self.timezone),
            'sunset': s['sunset'].astimezone(self.timezone),
            'dusk': s['dusk'].astimezone(self.timezone),
            'night-start': s['night-start'].astimezone(self.timezone)
        }

        current_time = self.current_time()

        output = (
            f"Time: {current_time}\n"
            f"Sun:\n"
            f"  Night-end: {sun_info['night-end'].strftime('%H:%M')}\n"
            f"  Dawn: {sun_info['dawn'].strftime('%H:%M')}\n"
            f"  Sunrise: {sun_info['sunrise'].strftime('%H:%M')}\n"
            f"  Noon: {sun_info['noon'].strftime('%H:%M')}\n"
            f"  Sunset: {sun_info['sunset'].strftime('%H:%M')}\n"
            f"  Dusk: {sun_info['dusk'].strftime('%H:%M')}\n"
            f"  Night-start: {sun_info['night-start'].strftime('%H:%M')}\n"
        )

        try:
            sys.stdout.write("\x1b[2J")
            sys.stdout.write("\x1b[H")
            sys.stdout.write(output + "\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"Error in output clearing: {e}")

        for key, time in enumerate(self.times):
            next_time = key + 1 if key + 1 < len(self.times) else 0
            if key == len(self.times) - 1:
                if (sun_info[time] < current_time) or (current_time < sun_info[self.times[next_time]]):
                    self.lights.color = self.smooth(time, self.times[next_time])
                    break
            elif sun_info[time] <= current_time < sun_info[self.times[next_time]]:
                self.lights.color = self.smooth(time, self.times[next_time])
                break

    def smooth(self, start, end):
        ratio = (self.current_time() - self._sun[start]).total_seconds() / (self._sun[end] - self._sun[start]).total_seconds()

        color = [0, 0, 0]
        for key in range(len(self.colors[start])):
            color[key] += self.colors[start][key] * (1 - ratio)
        for key in range(len(self.colors[end])):
            color[key] += self.colors[end][key] * ratio

        return color

    def current_time(self):
        if self.test:
            self.start += timedelta(minutes=0.25)
            return self.start
        else:
            return pytz.UTC.localize(self.tz_fix(datetime.now()))

    def tz_fix(self, dt):
        return dt.astimezone(self.timezone)

    @property
    def sun(self):
        s = sun(self.observer, self.current_time().date())
        for key in s:
            s[key] = self.tz_fix(s[key])
        s['night-end'] = s['dawn'] - timedelta(minutes=10)
        s['night-start'] = s['dusk'] + timedelta(minutes=10)
        return s

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        city = LocationInfo("", "", value["timezone"], value["latitude"], value["longitude"])
        self.observer = city.observer