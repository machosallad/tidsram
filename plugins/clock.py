#!/usr/bin/env python3

# Imports
import time
import numpy as np
import datetime
from plugins.abstract import AbstractSource
import json

layout = {
    "prefix": {
        "she": {"word": "HON", "index": 0},
        "is":  {"word": "ÄR", "index": 4},
        "soon": {"word": "SNART", "index": 7}
    },
    "minutes": {
        "five": {"word": "FEM", "index": 30},
        "ten": {"word": "TIO", "index": 18},
        "quarter": {"word": "KVART", "index": 30},
        "twenty": {"word": "TJUGO", "index": 24},
        "half": {"word": "HALV", "index": 44},
        "to": {"word": "I", "index": 40},
        "past": {"word": "ÖVER", "index": 36}
    },
    "hours": {
        "one": {"word": "ETT", "index": 48},
        "two": {"word": "TVÅ", "index": 50},
        "three": {"word": "TRE", "index": 53},
        "four": {"word": "FYRA", "index": 56},
        "five": {"word": "FEM", "index": 60},
        "six": {"word": "SEX", "index": 63},
        "seven": {"word": "SJU", "index": 66},
        "eight": {"word": "ÅTTA", "index": 72},
        "nine": {"word": "NIO", "index": 69},
        "ten": {"word": "TIO", "index": 84},
        "eleven": {"word": "ELVA", "index": 76},
        "twelve": {"word": "TOLV", "index": 80}
    },
    "day": {
        "monday": {"word": "M", "index": 132},
        "tuesday": {"word": "T", "index": 133},
        "wednesday": {"word": "O", "index": 134},
        "thursday": {"word": "T", "index": 135},
        "friday": {"word": "F", "index": 136},
        "saturday": {"word": "L", "index": 137},
        "sunday": {"word": "S", "index": 138}
    },
    "others": [
        {"word": "JMELIN", "index": 139}
        ]
}

def indexes(entry):
    word = entry["word"]
    index = entry["index"]
    length = len(word)
    return [*range(index,index+length)]

# Words to LED indexes mapping
words = {
    "prefix": {
        "she": [0, 1, 2],
        "is":  [4, 5],
        "soon": [7, 8, 9, 10, 11],
    },
    "minutes": {
        "five": [30, 31, 32],
        "ten": [18, 19, 20],
        "quarter": [12, 13, 14, 15, 16],
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

SIMULATE = True

class ClockSource(AbstractSource):
    def __init__(self, width=16, height=16):
        """Init the class"""
        super().__init__(width, height)
        self.fps = 10

        self._sim_hour = 0
        self._sim_minute = 0
        self._sim_second = 0
        self._sim_weekday = 0

        self.minutes = []
        self.hours = []
        self.weekdays = []
        self.prefix = []
        self.soon = []

        self.__construct_word_arrays()

        self._on_color = (255, 255, 255)
        self._off_color = (100, 100, 100)

    def __construct_word_arrays(self):
        self.prefix = [words["prefix"]["she"] + words["prefix"]["is"]]
        self.soon = [words["prefix"]["soon"]]

        self.minutes = [[],
                        indexes(layout["minutes"]["five"]) + words["minutes"]["past"],
                        words["minutes"]["ten"] + words["minutes"]["past"],
                        words["minutes"]["quarter"] + words["minutes"]["past"],
                        words["minutes"]["twenty"] + words["minutes"]["past"],
                        words["minutes"]["five"] + words["minutes"]["to"] +
                        words["minutes"]["half"],
                        words["minutes"]["half"],
                        words["minutes"]["five"] + words["minutes"]["past"] +
                        words["minutes"]["half"],
                        words["minutes"]["twenty"] + words["minutes"]["to"],
                        words["minutes"]["quarter"] + words["minutes"]["to"],
                        words["minutes"]["ten"] + words["minutes"]["to"],
                        words["minutes"]["five"] + words["minutes"]["to"],
                        []
                        ]
        self.hours = [
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
        self.weekdays = [
            words["day"]["monday"],
            words["day"]["tuesday"],
            words["day"]["wednesday"],
            words["day"]["thursday"],
            words["day"]["friday"],
            words["day"]["saturday"],
            words["day"]["sunday"]
        ]

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
        hour, minute, second, weekday = self.__getCurrentTime(
        ) if not SIMULATE else self.__getSimulateTime()
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
            self._sim_minute += 1
            self._sim_weekday += 1
            if self._sim_minute % 60 == 0:
                self._sim_second += 30

        return self._sim_hour % 24, self._sim_minute % 60, self._sim_second % 60, self._sim_weekday % 7

    def __constructIndexes(self, hour, minute, second, weekday):
        """Get array of indexes which map with words to light up."""
        # Check if an hour should be added
        additional_hour = 1 if (minute >= 35) else 0

        hour_index = hour % 12 + additional_hour
        minute_index = int(minute/5)

        strax = []
        if minute/5 % 1 > 0.7:
            minute_index += 1
            strax = self.soon[0]

        return self.prefix[0] + self.minutes[minute_index] + self.hours[hour_index] + self.weekdays[weekday] + strax

    def __construct_buffer(self, hour, minute, second, weekday):
        """Construct display buffer given the current time and weekday."""
        buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        led_indexes = self.__constructIndexes(hour, minute, second, weekday)

        index = 0
        for column in range(self.width):
            for row in range(self.height):
                if index in led_indexes:
                    buffer[column, row] = self.on_color
                else:
                    buffer[column, row] = self.off_color

                index += 1

        return buffer
