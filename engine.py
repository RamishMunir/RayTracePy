from config import *
import screen_drawquad
import material
import Spherebuffer
# import scene

class Engine:
    # draw
    def __init__(self, width:int, height:int):
        # screen
        self.screen_width = width
        self.screen_height = height

        # generate resources required
        self.makeAssets()
  
    def makeAssets(self):
        self.screen_quad = screen_drawquad.ScreenQuad()

        self.colorBuffer = material.Material(self.screen_width, self.screen_height)

        # fragment and vertex shader
        self.shader = self.createShader("shaders/vertexbuffer.glsl", "shaders/fragmentbuffer.glsl")

        # object buffer (doesnt only contain spheres)
        self.sphereBuffer = Spherebuffer.Buffer(1024 , 1)

        # compute shader
        self.Rayshader = self.makeComputeShader("shaders/raytracershader.glsl")
      
    def createShader(self, vertexFilepath, fragmentFilepath):
        # open shader file and compile it
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
        return shader

    def makeComputeShader(self, raytracerFilepath):
        # read and compile
        with open(raytracerFilepath, 'r') as f:
            compute_src = f.readlines()

        shader = compileProgram(compileShader(compute_src, GL_COMPUTE_SHADER))
        
        return shader 
    
    def updateScene(self, scene):

        scene.outDated = False

        glUseProgram(self.Rayshader)
        # use shader program just to be safe..
        # send data into the compute shader
        glUniform1f(glGetUniformLocation(self.Rayshader, "sphereCount"), len(scene.spheres))

        for i,_sphere in enumerate(scene.spheres):
            self.sphereBuffer.recordSphereMemory(i, _sphere)
    


        glUniform1f(glGetUniformLocation(self.Rayshader, "planeCount"), len(scene.planes))

        for i,_plane in enumerate(scene.planes):
            self.sphereBuffer.recordPlaneMemory(i+len(scene.spheres), _plane)

        self.sphereBuffer.readMemory()


    def makeScene(self, scene):

        glUseProgram(self.Rayshader)
        # use shader program just to be safe... 

        # send camera values to the compute shader
        glUniform3fv(glGetUniformLocation(self.Rayshader, "viewer.position"), 1, scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.Rayshader, "viewer.forwards"), 1, scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.Rayshader, "viewer.right"), 1, scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.Rayshader, "viewer.up"), 1, scene.camera.up)

        if (scene.outDated):
            self.updateScene(scene)

    def renderScene(self, scene):
        # drawing the objects
        glUseProgram(self.Rayshader)

        self.makeScene(scene)
        self.colorBuffer.writeTo()

        glDispatchCompute(int(self.screen_width/8), int(self.screen_height/8), 1)#x,y,z

        # make sure that rendering is finished before reading
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        self.drawScene()

    def drawScene(self):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.colorBuffer.readFrom()
        self.screen_quad.draw()
        pg.display.flip()


    def destroy(self):
        glDeleteProgram(self.Rayshader)
        self.screen_quad.destroy()
        self.colorBuffer.destroy()
        glDeleteProgram(self.shader)
