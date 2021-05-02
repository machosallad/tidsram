#!/usr/bin/env python3

import numpy as np
import sys
from display.abstract_display import AbstractDisplay
from neopixel import *

# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 64     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

class WS2812B(AbstractDisplay):
    def __init__(self, width=16, height=16):
        super().__init__(width, height)
        self._brightness = 0.3

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, ws.WS2811_STRIP_GRB)
        
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        
    def show(self, gamma=False):
        """ Iterate through the buffer and assign each LED index a color from the buffer"""
        index = 0
        for j in range(self.width):
            for i in range(self.height):
                color = Color(self.buffer[i][j][0].item(), self.buffer[i][j][1].item(), self.buffer[i][j][2].item())
                index = self.get_led_index(i,j)
                self.strip.setPixelColor(index,color)

        brightness = int(LED_BRIGHTNESS*self._brightness)
        self.strip.setBrightness(brightness)
        self.strip.show()
        return

    def get_led_index(self, x, y):
        """ Determines if the row is even or odd and returns a new index based on X and Y""" 
        pos = 0
        if x & 0x1:
            pos = x * self.height + (self.height - 1 - y)
        else:
            pos = x * self.height + y

        return pos

if __name__ == "__main__":
    display = WS2812B()
    display.create_test_pattern()
    display.show()
    import time
    time.sleep(5)
