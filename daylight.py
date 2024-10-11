from datetime import datetime, timezone, timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz
import sys

class Daylight(object):

    def __init__(self,config,rgb):
        self.config = config
        self.lights = rgb
        self._position = None
        self.position = self.config.get("position",{"timezone":"America/Phoenix","latitude":33.434061,"longitude":-112.016303})
        self.timezone = pytz.timezone(self.position['timezone'])
        self._sun = None
        self.timezone_hours=self.config.get("timezone_offset", 0)
        self.colors_default={
                "night-end": [0,0,0.05],
                "dawn": [0.1,0.1,0.3],
                "sunrise": [0.4,0.4,0.4],
                "noon": [1,1,1],
                "sunset": [0.5,0.25,0.1],
                "dusk": [0.3,0.1,0.4],
                "night-start": [0,0,0.05]
                }
        self.colors = self.config.get("colors",self.colors_default)
        self.times=['night-start',"dusk","sunset","noon","sunrise","dawn",'night-end']
        self.start = self.tz_fix(datetime.now())
        self.location = LocationInfo(self.position['timezone'], self.position['timezone'], self.position['latitude'], self.position['longitude'])
        self.test=False

    def set_color(self, color):
        self.lights.color = self.colors[color]

    def now(self):
        return self.tz_fix(datetime.now()).strftime("%Y-%m-%d %H:%M:%S.%f %z")[:-3]

    def update(self):
        s = sun(self.location.observer, date=self.now().date())
        sun_info = {
            'dawn': s['dawn'].astimezone(self.timezone),
            'sunrise': s['sunrise'].astimezone(self.timezone),
            'noon': s['noon'].astimezone(self.timezone),
            'sunset': s['sunset'].astimezone(self.timezone),
            'dusk': s['dusk'].astimezone(self.timezone),
            'night-start': s['dusk'].astimezone(self.timezone),
            'night-end': s['dawn'].astimezone(self.timezone)
        }

        # Output the current time and sun information all in one line.
        output = f"Time: {str(self.now())} | Sun: Dawn: {sun_info['dawn'].strftime('%H:%M')}, Sunrise: {sun_info['sunrise'].strftime('%H:%M')}, Noon: {sun_info['noon'].strftime('%H:%M')}, Sunset: {sun_info['sunset'].strftime('%H:%M')}, Dusk: {sun_info['dusk'].strftime('%H:%M')}"

        # Use '\r' to return to the beginning and ensure the entire line is cleared with end spaces
        # Calculate additional space needed to clear previous output
        needed_space = max(80 - len(output), 0)
        sys.stdout.write("\r" + output + " " * needed_space)
        sys.stdout.flush()

        # Handle night wrap around before loop
        # TODO: Smooth transition is broken because they keep the same day
        if self.now() > sun_info['night-start'] or self.now() < sun_info['night-end']:
            self.lights.color = self.smooth("night-start","night-end")
            return
        
        # Find color block to smooth
        for key in range(len(self.times)):
            if self.now() > sun_info[self.times[key]]:
                self.lights.color = self.smooth(self.times[key],self.times[key-1])
                break


    def smooth(self,start,end):
        # Percentage of mix between times
        ratio = (self.now()-self.sun[start]).total_seconds() / (self.sun[end]-self.sun[start]).total_seconds()

        # Mix start and end colors based on ratio
        color = [0,0,0]
        for key in range(len(self.colors[start])):
            color[key] +=  self.colors[start][key]*(1-ratio)
        for key in range(len(self.colors[end])):
            color[key] +=  self.colors[end][key]*ratio
       
        #print("Ratio ("+start+"/"+end+"): " + str(ratio))
        return color


    def now(self):
        if self.test:
            self.start += timedelta(minutes=0.25)
            return self.start
        else:
            # Return timezone corrected now
            return pytz.UTC.localize(self.tz_fix(datetime.now()))

    def tz_fix(self, dt):
        return dt.astimezone(self.timezone)

    @property
    def sun(self):
        s = sun(self.observer, self.now())
        for key in s:
            s[key] = self.tz_fix(s[key])
        # Workaround for dawn and dusk colors
        # TODO: Add time between horizon and degree position instead?
        s['night-end']=s['dawn']-timedelta(minutes=10)
        s['night-start']=s['dusk']+timedelta(minutes=10)
        return s

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        city = LocationInfo("","",value["timezone"],value["latitude"],value["longitude"])
        self.observer = city.observer

