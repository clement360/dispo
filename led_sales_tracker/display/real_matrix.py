import numpy as np
from .base import BaseDisplay, ROWS, COLS

class RealMatrixDisplay(BaseDisplay):
    def __init__(self):
        super().__init__()
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
        opts = RGBMatrixOptions()
        opts.rows = ROWS
        opts.cols = COLS
        self.matrix = RGBMatrix(options=opts)

    def push(self):
        # expect buffer as numpy (H, W, 3)
        for y in range(ROWS):
            for x in range(COLS):
                r, g, b = map(int, self.buffer[y, x])
                self.matrix.SetPixel(x, y, r, g, b)