#!/usr/bin/env python3

# Imports
import time
import numpy as np
import datetime
from plugins.abstract import AbstractSource
import json

# Words to LED indexes mapping
words = {
    "prefix": {
        "she": [0,1,2],
        "is":  [4,5],
        "soon": [7,8,9,10,11],
    },
    "minutes": {
        "five": [30, 31, 32],
        "ten": [18, 19, 20],
        "quarter": [12,13,14,15,16],
        "twenty": [24, 25, 26, 27, 28],
        "half": [44, 45, 46, 47],
        "to": [40],
        "past": [36, 37, 38, 39]
    },
    "hours": {
        "one": [48, 49, 50],
        "two": [50, 51, 52],
        "three": [53, 54, 55],
        "four": [56, 57, 58, 59],
        "five": [60, 61, 62],
        "six": [63, 64, 65],
        "seven": [66, 67, 68],
        "eight": [72, 73, 74, 75],
        "nine": [69, 70, 71],
        "ten": [84, 85, 86],
        "eleven": [76, 77, 78, 79],
        "twelve": [80, 81, 82, 83]
    },
    "day": {
        "monday": [132],
        "tuesday": [133],
        "wednesday": [134],
        "thursday": [135],
        "friday": [136],
        "saturday": [137],
        "sunday": [138],
    }
}

prefix = [words["prefix"]["she"] + words["prefix"]["is"]]
soon = [words["prefix"]["soon"]]

minutes = [[],
           words["minutes"]["five"] + words["minutes"]["past"],
           words["minutes"]["ten"] + words["minutes"]["past"],
           words["minutes"]["quarter"] + words["minutes"]["past"],
           words["minutes"]["twenty"] + words["minutes"]["past"],
           words["minutes"]["five"] + words["minutes"]["to"] + words["minutes"]["half"],
           words["minutes"]["half"],
           words["minutes"]["five"] + words["minutes"]["past"] + words["minutes"]["half"],
           words["minutes"]["twenty"] + words["minutes"]["to"],
           words["minutes"]["quarter"] + words["minutes"]["to"],
           words["minutes"]["ten"] + words["minutes"]["to"],
           words["minutes"]["five"] + words["minutes"]["to"],
           []
           ]
hours = [
    words["hours"]["twelve"],
    words["hours"]["one"],
    words["hours"]["two"],
    words["hours"]["three"],
    words["hours"]["four"],
    words["hours"]["five"],
    words["hours"]["six"],
    words["hours"]["seven"],
    words["hours"]["eight"],
    words["hours"]["nine"],
    words["hours"]["ten"],
    words["hours"]["eleven"],
    words["hours"]["twelve"]
]

weekdays = [
    words["day"]["monday"],
    words["day"]["tuesday"],
    words["day"]["wednesday"],
    words["day"]["thursday"],
    words["day"]["friday"],
    words["day"]["saturday"],
    words["day"]["sunday"]
]

SIMULATE = True

class ClockSource(AbstractSource):
    def __init__(self, width=16, height=16):
        """Init the class"""
        super().__init__(width, height)
        self.fps = 20

        self._sim_hour = 0
        self._sim_minute = 0
        self._sim_second = 0
        self._sim_weekday = 0

        self._on_color = (255,255,255)
        self._off_color = (100,100,100)

    @property
    def on_color(self):
        return self._on_color

    @on_color.setter
    def on_color(self, color):
        self._on_color = color

    @property
    def off_color(self):
        return self._off_color

    @off_color.setter
    def off_color(self, color):
        self._off_color = color

    def update(self, dt):
        """Update the source. Checks current time and refreshes the internal buffer."""
        hour, minute, second, weekday = self.__getCurrentTime() if not SIMULATE else self.__getSimulateTime()
        self._buffer = self.__construct_buffer(hour, minute, second, weekday)

    def __getCurrentTime(self):
        """Get current time information."""
        now = datetime.datetime.now().time()
        weekday = datetime.datetime.now().weekday()
        return now.hour, now.minute, now.second, weekday

    def __getSimulateTime(self):
        """Get simulated time information."""
        self._sim_hour += 1
        if self._sim_hour % 24 == 0:
            self._sim_minute +=1
            self._sim_weekday +=1
            if self._sim_minute % 60 == 0:
                self._sim_second +=30

        return self._sim_hour % 24, self._sim_minute % 60, self._sim_second % 60, self._sim_weekday % 7

    def __constructIndexes(self, hour, minute, second, weekday):
        """Get array of indexes which map with words to light up."""
        # Check if an hour should be added
        additional_hour = 1 if (minute >= 35) else 0
        
        hour_index = hour % 12 + additional_hour
        minute_index = int(minute/5)

        strax = []
        if minute/5 % 1 > 0.7: 
            minute_index +=1
            strax = soon[0]

        return prefix[0] + minutes[minute_index] + hours[hour_index] + weekdays[weekday] + strax

    def __construct_buffer(self, hour, minute, second, weekday):
        """Construct display buffer given the current time and weekday."""
        buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        led_indexes = self.__constructIndexes(hour,minute,second,weekday)

        index = 0
        for column in range(self.width):
            for row in range(self.height):
                if index in led_indexes:
                    buffer[column, row] = self.on_color
                else:
                    buffer[column, row] = self.off_color

                index += 1

        return buffer
