#!python3

import board
import neopixel

class RGB(object):

    def __init__(self,config,r=None,g=None,b=None):
        self.config=config
        self._white_balance = self.config.get("white_balance",[1,1,1])
        self._intensity = self.config.get("intensity",1)
        self.ws = self.config.get("led_ws",{"enable":1,"pin":"D18","count":20,"brightness":0.5})
        self.led_pins = self.config.get("led_pins",{"r":22,"g":27,"b":17})
        self._color = [0,0,0]

        if self.ws["enable"]:
            self.pixels = neopixel.NeoPixel(
                getattr(board, self.ws["pin"]),
                self.ws["count"],
                brightness=self.ws["brightness"],
                auto_write=False
            )
        else:
            self.pixels = None

    def set(self):
        r = self.color[0] * self.white_balance[0] * self.intensity
        g = self.color[1] * self.white_balance[1] * self.intensity
        b = self.color[2] * self.white_balance[2] * self.intensity

        if(self.ws["enable"]):
            r = max(0, min(255, int(r * 255)))
            g = max(0, min(255, int(g * 255)))
            b = max(0, min(255, int(b * 255)))
            self.pixels.fill((r, g, b))
            self.pixels.show()
        else:
            with open('/dev/pi-blaster', 'w') as pwm:
                pwm.write(f"{self.led_pins['r']}={r} ")
                pwm.write(f"{self.led_pins['g']}={g} ")
                pwm.write(f"{self.led_pins['b']}={b}\n")

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.set()

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = value
        self.set()

    @property
    def white_balance(self):
        return self._white_balance

    @white_balance.setter
    def white_balance(self, value):
        self._white_balance = value
        self.set()
