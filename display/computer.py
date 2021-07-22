#!/usr/bin/env python3
import configparser
import sys
import pygame
import random
import json

from display.abstract_display import AbstractDisplay
from array import *

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARKGRAY = (20, 20, 20)
WHITE = (255, 255, 255)


class Computer(AbstractDisplay):
    def __init__(self, width=12, height=12, margin=5, size=50):
        super().__init__(width, height)

        self.margin = margin
        self.size = size

        self.window_size = (
            width * size + (width + 1) * margin,
            height * size + (height + 1) * margin,
        )

        pygame.init()
        pygame.font.init()

        self.config = configparser.ConfigParser()
        self.config.read("settings.conf")

        self.fill_empty = self.config.getboolean("tidsram_computer", "fill_empty")
        self.show_index = self.config.getboolean("tidsram_computer", "show_index")

        # Load fonts
        self.index_font = pygame.font.SysFont("arial", 12)
        self.char_font = pygame.font.Font("fonts/D-DINExp-Bold.ttf", self.size)

        # Prepare word list
        self.words = []
        for i in range(self.width * self.height):
            self.words.append("")

        # Load layout
        layout = self.config.get("tidsram_display", "layout")
        f = open(layout, encoding="utf-8")
        layout = json.load(f)

        # Read layout words
        for category in layout:
            for words in layout[category]:
                word = layout[category][words]["word"]
                index = int(layout[category][words]["index"])
                for char in word:
                    self.words[index] = char
                    index += 1

        # Add random letters to empty slots
        if self.fill_empty:
            for i in range(self.width * self.height):
                if self.words[i] == "":
                    uppercase = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
                    self.words[i] = random.choice(uppercase)

        # Create the window
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("tidsram {}x{}".format(width, height))
        self.show()

    def show(self, gamma=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        index = 0
        for j in range(self.width):
            for i in range(self.height):
                color = self.buffer[i][j] * self.brightness

                # Draw background color and border
                pygame.draw.rect(
                    self.surface,
                    DARKGRAY,
                    [
                        (self.margin + self.size) * j + self.margin,
                        (self.margin + self.size) * i + self.margin,
                        self.size,
                        self.size,
                    ],
                )

                # Draw characters from words array
                character = self.char_font.render(
                    self.words[i * self.width + j], True, color
                )
                self.surface.blit(
                    character,
                    [
                        (self.margin + self.size) * j + self.margin * 3,
                        (self.margin + self.size) * i + self.margin,
                        self.size,
                        self.size,
                    ],
                )

                # Draw index number of current character
                if self.show_index:
                    index_as_img = self.index_font.render(
                        str(i * self.width + j), True, WHITE
                    )
                    self.surface.blit(
                        index_as_img,
                        [
                            (self.margin + self.size) * j + self.margin,
                            (self.margin + self.size) * i + self.margin,
                            self.size,
                            self.size,
                        ],
                    )

        pygame.display.update()

        return


if __name__ == "__main__":
    display = Computer()
    # display.run_benchmark()
    display.create_test_pattern()
    display.show()
    import time

    time.sleep(10)
