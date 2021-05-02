#!/usr/bin/env python3

import abc
import numpy as np
import time
from enum import Enum

class AbstractSource(abc.ABC):
    def __init__(self,width=16, height=16):
        self.width = width
        self.height = height
        self.number_of_pixels = self.height * self.width
        self._buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.fps = 0
    
    @property
    def buffer(self):
        """The buffer contains the rgb data representation of the source."""
        return self._buffer

    def clear_buffer(self):
        """Clear the source buffer by filling it with zeros."""
        self._buffer = np.zeros_like(self._buffer)

    @abc.abstractmethod
    def update(self,dt):
        """Update the source by passing current dt."""
