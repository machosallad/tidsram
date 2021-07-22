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
from plugins.clock import ClockPlugin
import paho.mqtt.client as mqtt

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

        # Sources
        self.source = ClockPlugin(DISPLAY_HEIGTH,DISPLAY_HEIGTH)
        self.display.brightness = 1

    # The callback for when the client receives a CONNACK response from the server.
    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribe to topics from the display
        for topic in self.display.topics:
            client.subscribe(topic)

        # Subscribe to topics from plugins
        for topic in self.source.topics:
            client.subscribe(topic)
        
        # Add callback for the display
        client.message_callback_add(self.display.subscription_filter, self.display.callback)

        # Add callback for plugins using filter
        client.message_callback_add(self.source.subscription_filter,self.source.callback)

    # The callback for when a PUBLISH message is received from the server.
    def on_mqtt_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def mainloop(self):
        # Prepare and start loading resources

        # MQTT
        client = mqtt.Client()
        client.on_connect = self.on_mqtt_connect
        client.on_message = self.on_mqtt_message
        client.connect("localhost")
        client.loop_start()

        # Timer
        clock = pygame.time.Clock()

        while True:
            # Update the display buffer
            self.display.buffer = self.source.buffer

            # Render the frame
            self.display.show()

            # Limit CPU usage do not go faster than FPS
            dt = clock.tick(self.source.fps)

            self.source.update(dt)

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
