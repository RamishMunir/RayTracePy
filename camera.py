from config import *

# camera class --> position, forwards direction(x), right direction(y), up direction as vectors(z)
class Camera:

    def __init__(self, position):

        self.position = np.array(position, dtype=np.float32)

        self.recalculateVectors()
    
    # might be useful in the future when the camera position changes
    def recalculateVectors(self):

        self.forwards = np.array([1.0,0.0,0.0], dtype=np.float32)


        self.right = pyrr.vector3.cross(self.forwards, np.array([0,0,1],dtype=np.float32))

        self.up = pyrr.vector3.cross(self.right, self.forwards)

