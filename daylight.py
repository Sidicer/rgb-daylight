from datetime import datetime, timedelta
from astral import Observer
from astral.sun import sun
from rgb import RGB
import pytz


class Daylight(object):

    def __init__(self,rgb):
        self.lights = rgb
        self._position = [0,0,0]
        self._sun = None
        self.timezone_hours=0
        self.colors={
                "night-end": [0,0,0.1],
                "dawn": [0.1,0.1,0.3],
                "sunrise": [0.4,0.4,0.4],
                "noon": [1,1,1],
                "sunset": [0.5,0.25,0.1],
                "dusk": [0.3,0.1,0.4],
                "night-start": [0,0,0.1]
                }
        self.times=['night-start',"dusk","sunset","noon","sunrise","dawn",'night-end']


    def update(self):
        print("Time: " +str(self.now()))
        # Handle night wrap around before loop
        if self.now() > self.sun['night-start'] or self.now() < self.sun['night-end']:
            self.lights.color = self.smooth("night-start","night-end")
            return
        
        # Find color block to smooth
        for key in range(len(self.times)):
            if self.now() > self.sun[self.times[key]]:
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
       
        print("Ratio ("+start+"/"+end+"): " + str(ratio))
        return color


    def now(self):
        # Return timezone corrected now
        return pytz.UTC.localize(self.tz_fix(datetime.now()))


    def tz_fix(self,utc_time):
        # Fix datetime timezone
        #TODO: There must be a datetime and not timedelta method instead
        return utc_time + timedelta(hours=self.timezone_hours, minutes=0)


    @property
    def sun(self):
        s = sun(self.observer, self.now())
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
        self._postion = value
        self.observer = Observer(self.position[0],self.position[1],self.position[2])

