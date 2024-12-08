import time
class FPS():
    def __init__(self, maxFpsLen = 255):
        self.timeNow = time.time()
        self.fps = 0
        self.fpsLen = 0
        self.maxFpsLen = maxFpsLen
    
    def calc(self) -> None:
        timeNow = time.time()
        dt = 1/(timeNow-self.timeNow)
        self.fpsLen += 1
        
        if self.fpsLen > self.maxFpsLen:
            self.fpsLen = 1
        
        self.fps = self.fps+(dt-self.fps)/self.fpsLen
        self.timeNow = timeNow