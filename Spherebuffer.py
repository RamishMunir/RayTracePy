from config import *


class Buffer:

# size of buffer and the binding number as the input
    def __init__(self, size, bindnum):
        
        self.binding = bindnum
        self.size =size

        # sphere
        #  center = (x, y, z), radius, color = (r, g, b, -) 
        # pixel 1 = (x, y, z, radius), pixel 2 = (r, g, b, _), pixel 3 = (-, -, -, -), pixel 4: (- - - -) Pixel 5: (- - - -)

        # plane
        # center= (x, y, z), tangent = (tx ty tz), bitangent = (bx, by, bz), normal= (x, y, z), (uMin, uMax, vMin, vMax) , color (r, g, b, -) 
        # pixel 1: memory = (cx, cy, cz, yx) pixel 2: (ty, tz, bx, by) pixel 3: (bz, nx, ny, nz) pixel 4: (uMin, uMax, vMin, vMax) pixel 5: (r, g, b, -)

        # five pixel each with 4 attributes (5 * 4 = 20)
        # initialize it with zeros
        self.objectMemory = np.zeros( 20 * size, dtype=np.float32 )

        self.texture = glGenTextures(1)
        # bind as current texture working with

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,GL_REPEAT)  # S-T coordinate pairs
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # no sampling
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F,5 , size,  0, GL_RGBA, GL_FLOAT, bytes(self.objectMemory))
        

    def recordSphereMemory(self, i, _sphere):
    #  make a huge list which contains the x,y,z, radius , color of each sphere
        if i>=self.size:
            return 
        
        index = i *20

        self.objectMemory[index:index+3] = _sphere.center[:]
        self.objectMemory[index+3] = _sphere.radius
        self.objectMemory[index+4: index+7 ] = _sphere.color[:]

    def recordPlaneMemory(self, i, _plane):

        if i>=self.size:
            return

        index = i * 20

        self.objectMemory[index:index+3] = _plane.center[:]
        self.objectMemory[index+3: index+6] = _plane.tangent[:]
        self.objectMemory[index+6: index+9] = _plane.bitangent[:]
        self.objectMemory[index+9: index+12] = _plane.normal[:]

        self.objectMemory[index+12] = _plane.uMin
        self.objectMemory[index+13] = _plane.uMax
        self.objectMemory[index+14] = _plane.vMin
        self.objectMemory[index+15] = _plane.vMax

        self.objectMemory[index+16: index+19] = _plane.color[:]



    def readMemory(self):

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 5, self.size,  0, GL_RGBA, GL_FLOAT, bytes(self.objectMemory))
        glBindImageTexture(1, self.texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)



    def destroy(self):

        glDeleteTextures(1, (self.texture,))
