from config import *

class Sphere:
    
    # center coordinates, radius and color
    def __init__(self, center, radius, color ):

        self.center = np.array(center, dtype= np.float32)
        self.color = np.array(color, dtype= np.float32)
        self.radius = radius