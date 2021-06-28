#!/user/bin/env python3
"""
Main entry point of the tidsram project.
Runs the main game-loop.
"""

# Imports
import os
import platform
import sys
import abc
import numpy as np
import time
import pygame
import io
from io import BytesIO
from pathlib import Path
from plugins.clock import ClockSource

# Global variables
DISPLAY_WIDTH = 12
DISPLAY_HEIGTH = 12

class WordClock():

    def __init__(self):
        # Change working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        if is_raspberrypi():
            from display.ws2812b import WS2812B
            self.display = WS2812B(DISPLAY_WIDTH,DISPLAY_HEIGTH)
        else:
            from display.computer import Computer
            self.display = Computer(DISPLAY_WIDTH, DISPLAY_HEIGTH,5,50)
      
    def mainloop(self):
        # Prepare and start loading resources
        clock = pygame.time.Clock()       
        source = ClockSource(DISPLAY_HEIGTH,DISPLAY_HEIGTH)
        self.display.brightness = 1

        while True:
            # Update the display buffer
            self.display.buffer = source.buffer
            
            # Render the frame
            self.display.show()

            # Limit CPU usage do not go faster than FPS
            dt = clock.tick(source.fps)
            
            source.update(dt)
        return

# Function declarations

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

# Main body
if __name__ == "__main__":
    wordclock = WordClock()
    wordclock.display.show()

    wordclock.mainloop()
