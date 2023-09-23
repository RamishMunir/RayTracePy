from config import *

class Mesh:

    def __init__(self):
    
        self.vertex_count = 0

         # vertex array object, declare vertex data, associates itself with vbo
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        # vertex buffer object, generate one buffer and tell us the index
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

    def draw(self):

        glBindVertexArray(self.vao)  # bind vertex attribute array
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):

        # free memory
        # extra comma to declare its a list or tuple
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))