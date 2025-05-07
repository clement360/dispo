from abc import ABC, abstractmethod
import numpy as np
from .font5x7 import FONT

ROWS, COLS = 32, 64  # keep global for font & helpers

class BaseDisplay(ABC):
    """
    Drivers work with an RGB pixel buffer shaped (ROWS, COLS, 3).
    Colours are 0-255 ints.
    """

    def __init__(self):
        self.buffer = np.zeros((ROWS, COLS, 3), dtype=np.uint8)

    @abstractmethod
    def push(self):
        """Send current buffer to the physical / emulated matrix."""
        pass

    def clear(self, colour=(0, 0, 0)):
        self.buffer[:, :] = colour

    # Optional helper to draw text
    def draw_text(self, text, x, y, colour=(255, 255, 255)):
        for char in text:
            glyph = FONT.get(char, FONT['?'])
            for row in range(7):
                for col in range(5):
                    if glyph[row] & (1 << (4 - col)):
                        px = x + col
                        py = y + row
                        if 0 <= px < COLS and 0 <= py < ROWS:
                            self.buffer[py, px] = colour
            x += 6  # 5 pixels + 1 space

    def draw_series(self, series, x, y, colour=(255, 255, 255)):
        """
        Draw a series of data points on the display.
        :param series: List of tuples (x, y) representing the data points.
        :param x: Starting x position.
        :param y: Starting y position.
        :param colour: Colour of the points.
        """
        # Create darker version of the color (50% brightness)
        darker_colour = tuple(max(0, c // 2) for c in colour)

        for point in series:
            px = x + point[0]
            py = y + point[1]
            
            if 0 <= px < COLS and 0 <= py < ROWS:
                self.buffer[py, px] = colour
                for fill_y in range(py + 1, ROWS):
                    self.buffer[fill_y, px] = darker_colour
                
    def set_pixel(self, x, y, colour=(255, 255, 255)):
        """
        Set a single pixel in the buffer to the specified color.
        
        Parameters:
        x (int): X coordinate (column)
        y (int): Y coordinate (row)
        colour (tuple): RGB color tuple with values 0-255
        
        Returns:
        None
        """
        if 0 <= x < COLS and 0 <= y < ROWS:
            self.buffer[y, x] = colour