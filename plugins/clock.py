#!/usr/bin/env python3

# Imports
import time
import numpy as np
import datetime
from plugins.abstract import AbstractPlugin
import json
import configparser
from PIL import ImageColor

def indexes(entry):
    """Words to LED indexes mapping."""
    word = entry["word"]
    index = entry["index"]
    length = len(word)
    return [*range(index, index + length)]


def rgb2hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


class ClockPlugin(AbstractPlugin):
    def __init__(self, width=16, height=16):
        """Init the class"""
        super().__init__(width, height)
        self.config = configparser.ConfigParser()
        self.config.read("settings.conf")
        self.section = "tidsram_clock"

        self.fps = 5

        self._sim_hour = 0
        self._sim_minute = 0
        self._sim_second = 0
        self._sim_weekday = 0

        self.minutes = []
        self.hours = []
        self.weekdays = []
        self.prefix = []
        self.soon = []
        self.signature = []
        self.simulate = self.config.getboolean(self.section, "simulate")
        self._on_color = ImageColor.getcolor(self.config.get(self.section, "on_rgb"), "RGB")
        self._off_color = ImageColor.getcolor(self.config.get(self.section, "off_rgb"), "RGB")
        self._day_color = ImageColor.getcolor(self.config.get(self.section, "day_rgb"), "RGB")
        self._signature_color = ImageColor.getcolor(self.config.get(self.section, "signature_rgb"), "RGB")

        self.__construct_word_arrays()

    def __construct_word_arrays(self):
        f = open("layouts/swedish3.json", encoding="utf-8")
        layout = json.load(f)

        self.prefix = indexes(layout["prefix"]["she"]) + indexes(layout["prefix"]["is"])
        self.soon = indexes(layout["prefix"]["soon"])
        self.signature = indexes(layout["others"]["signature"])

        self.minutes = [
            [],
            indexes(layout["minutes"]["five"]) + indexes(layout["minutes"]["past"]),
            indexes(layout["minutes"]["ten"]) + indexes(layout["minutes"]["past"]),
            indexes(layout["minutes"]["quarter"]) + indexes(layout["minutes"]["past"]),
            indexes(layout["minutes"]["twenty"]) + indexes(layout["minutes"]["past"]),
            indexes(layout["minutes"]["five"])
            + indexes(layout["minutes"]["to"])
            + indexes(layout["minutes"]["half"]),
            indexes(layout["minutes"]["half"]),
            indexes(layout["minutes"]["five"])
            + indexes(layout["minutes"]["past"])
            + indexes(layout["minutes"]["half"]),
            indexes(layout["minutes"]["twenty"]) + indexes(layout["minutes"]["to"]),
            indexes(layout["minutes"]["quarter"]) + indexes(layout["minutes"]["to"]),
            indexes(layout["minutes"]["ten"]) + indexes(layout["minutes"]["to"]),
            indexes(layout["minutes"]["five"]) + indexes(layout["minutes"]["to"]),
            [],
        ]
        self.hours = [
            indexes(layout["hours"]["twelve"]),
            indexes(layout["hours"]["one"]),
            indexes(layout["hours"]["two"]),
            indexes(layout["hours"]["three"]),
            indexes(layout["hours"]["four"]),
            indexes(layout["hours"]["five"]),
            indexes(layout["hours"]["six"]),
            indexes(layout["hours"]["seven"]),
            indexes(layout["hours"]["eight"]),
            indexes(layout["hours"]["nine"]),
            indexes(layout["hours"]["ten"]),
            indexes(layout["hours"]["eleven"]),
            indexes(layout["hours"]["twelve"]),
        ]
        self.weekdays = [
            indexes(layout["day"]["monday"]),
            indexes(layout["day"]["tuesday"]),
            indexes(layout["day"]["wednesday"]),
            indexes(layout["day"]["thursday"]),
            indexes(layout["day"]["friday"]),
            indexes(layout["day"]["saturday"]),
            indexes(layout["day"]["sunday"]),
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

    @property
    def day_color(self):
        return self._day_color

    @day_color.setter
    def day_color(self, color):
        self._day_color = color

    @property
    def signature_color(self):
        return self._signature_color

    @signature_color.setter
    def signature_color(self, color):
        self._signature_color = color

    @property
    def topics(self):
        return ["tidsram/plugin/clock/on", "tidsram/plugin/clock/off", "tidsram/plugin/clock/day", "tidsram/plugin/clock/signature"]

    @property
    def subscription_filter(self):
        return "tidsram/plugin/clock/#"

    def callback(self, client, userdata, msg):
        print("%s %s" % (msg.topic, msg.payload))

        try:
            color = ImageColor.getcolor(msg.payload.decode("utf-8"), "RGB")
            if msg.topic == "tidsram/plugin/clock/on":
                self.on_color = color
                self.config.set(self.section, "on_rgb", rgb2hex(self.on_color))
            elif msg.topic == "tidsram/plugin/clock/off":
                self.off_color = color
                self.config.set(self.section, "off_rgb", rgb2hex(self.off_color))
            elif msg.topic == "tidsram/plugin/clock/day":
                self._day_color = color
                self.config.set(self.section, "day_rgb", rgb2hex(self.day_color))
            elif msg.topic == "tidsram/plugin/clock/signature":
                self._signature_color = color
                self.config.set(self.section, "signature_rgb", rgb2hex(self.signature_color))
        except ValueError as ve:
            print("Invalid RGB value")

        with open("settings.conf", "w") as configfile:
            self.config.write(configfile)

    def update(self, dt):
        """Update the source. Checks current time and refreshes the internal buffer."""
        hour, minute, second, weekday = (
            self.__getCurrentTime() if not self.simulate else self.__getSimulateTime()
        )
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

        return (
            self._sim_hour % 24,
            self._sim_minute % 60,
            self._sim_second % 60,
            self._sim_weekday % 7,
        )

    def __constructIndexes(self, hour, minute, second, weekday):
        """Get array of indexes which map with words to light up."""
        # Check if an hour should be added
        additional_hour = 1 if (minute >= 24) else 0

        hour_index = hour % 12 + additional_hour
        minute_index = int(minute / 5)

        soon = []
        if minute / 5 % 1 > 0.7:
            minute_index += 1
            soon = self.soon

        return (
            self.prefix
            + self.minutes[minute_index]
            + self.hours[hour_index]
            + self.weekdays[weekday]
            + soon
            + self.signature
        )

    def __construct_buffer(self, hour, minute, second, weekday):
        """Construct display buffer given the current time and weekday."""
        buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        led_indexes = self.__constructIndexes(hour, minute, second, weekday)

        index = 0
        for column in range(self.width):
            for row in range(self.height):
                if index in led_indexes:
                    if index in range(139, 144):
                        buffer[column, row] = self.signature_color
                    elif index in range(132, 139):
                        buffer[column, row] = self.day_color
                    else:
                        buffer[column, row] = self.on_color
                else:
                    buffer[column, row] = self.off_color

                index += 1

        return buffer
