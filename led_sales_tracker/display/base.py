from abc import ABC, abstractmethod
import numpy as np

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
        from .font5x7 import FONT
        for char in text.upper():
            glyph = FONT.get(char, FONT['?'])
            for row in range(7):
                for col in range(5):
                    if glyph[row] & (1 << (4 - col)):
                        px = x + col
                        py = y + row
                        if 0 <= px < COLS and 0 <= py < ROWS:
                            self.buffer[py, px] = colour
            x += 6  # 5 pixels + 1 space