from config import *
import scene
import engine

class App:

    def __init__(self):
        """ Initialise the program """
        # initialise pygame
        self.screenwidth = 800
        self.screenheight = 600

        self.startpygame()

        self.scene = scene.Scene()
        self.graphicsEngine = engine.Engine(self.screenwidth, self.screenheight)

        self.setTimer()

        self.mainLoop()

    def startpygame(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenwidth, self.screenheight), pg.OPENGL | pg.DOUBLEBUF)
        
        self.lightCount = 0


    def setTimer(self):
        # Framerate timer
        # initialize variable to calculate framerate
        self.LastTime = pg.time.get_ticks()
        self.CurrentTime = pg.time.get_ticks()
        self.numFrames = 0
        self.frameTime = 0


    def mainLoop(self):
        """ Run the app """

        running = True
        while (running):
            # check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False

                elif event.type == pg.KEYDOWN:
                  if event.key == pg.K_ESCAPE:
                    running = False

            # render
            self.graphicsEngine.renderScene(self.scene)

            # frame
            self.calculateFramerate()

        self.quit()

    def calculateFramerate(self):

        self.CurrentTime= pg.time.get_ticks()
        diff = self.CurrentTime - self.LastTime
        if (diff>= 1000):
            framerate = max(1, int(1000.0 * self.numFrames/diff))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.LastTime = self.CurrentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1, framerate)) 
        self.numFrames +=1



    def quit(self):

        pg.quit()


        