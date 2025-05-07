import pygame
from .base import BaseDisplay, ROWS, COLS

CELL_PITCH = 10  # Distance between LED centers (pixels)
LED_DIAMETER = 8 # Diameter of the LED “beads” (pixels)
LED_RADIUS = LED_DIAMETER // 2
BG_COLOR = (20, 20, 20)  # Panel background

class EmulatedMatrixDisplay(BaseDisplay):
    def __init__(self):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((COLS * CELL_PITCH, ROWS * CELL_PITCH))
        pygame.display.set_caption("LED Matrix Emulator")

    def initialize(self):
        # (Optional - keep for interface compatibility)
        pass

    def push(self):
        # Pump events so window stays responsive
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
        self.screen.fill(BG_COLOR)
        for y in range(ROWS):
            for x in range(COLS):
                colour = tuple(self.buffer[y, x])
                center = (x * CELL_PITCH + CELL_PITCH // 2, y * CELL_PITCH + CELL_PITCH // 2)
                pygame.draw.circle(self.screen, colour, center, LED_RADIUS)
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()