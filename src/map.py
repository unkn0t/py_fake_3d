import numpy as np

class Map:
    def __init__(self, data: str, width: int, height: int):
        self.width = width
        self.height = height
            
        self.data = np.zeros((height, width), np.int32)
        for row in range(height):
            for col in range(width):
                index = row * width + col
                self.data[row, col] = int(data[index])

    def is_wall(self, x: int, y: int) -> bool:
        return self.data[y, x] > 0
