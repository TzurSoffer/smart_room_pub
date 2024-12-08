import time

class Timer:
    def __init__(self):
        self.timeNow = time.time()
    
    def reset(self):
        self.timeNow = time.time()
    
    def waitRemainingTime(self, targetTime) -> None:
        time.sleep(targetTime-(time.time()-self.timeNow))
        self.reset()
    
    def isTimeUp(self, targetTime) -> bool:
        return(time.time()-self.timeNow > targetTime)