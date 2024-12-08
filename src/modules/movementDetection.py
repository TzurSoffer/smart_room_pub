import numpy as np
import time

class ChangeDetection():
    def __init__(self, chgThresh = 100, noiseThresh = 10):
        self.thresh = chgThresh
        self.bgThresh = noiseThresh
        self.frame_Z1 = ""
        self._isChange = False

    def _removeNoise(self, matrix, thresh=3, start=0, delete=False): #< 7 is good for thresh
        if delete == False:
            matrix[np.where(((matrix > start-thresh)&(matrix < start+thresh)))] = start
        else:
            matrix = np.delete(matrix, np.where(((matrix > start-thresh)&(matrix < start+thresh))))
        return(matrix)

    def isChange(self, frame):
        if type(self.frame_Z1) != str:
            diff = np.abs(np.subtract(self.frame_Z1, frame, dtype=np.int16))
            diff = diff.astype(np.uint8)

            if self.bgThresh > 0:
                diff = self._removeNoise(diff, thresh=self.bgThresh)

            if np.sum(diff) > self.thresh:
                self._isChange = True
            else:
                self._isChange = False

        self.frame_Z1 = frame

        return(self._isChange)

class InRoomDetection(ChangeDetection):
    def __init__(self, outAfter = 4, chgThresh = 100, noiseThresh = 10):
        super().__init__(chgThresh = chgThresh, noiseThresh = noiseThresh)
        self.timeNow = 0
        self.outAfter = int(outAfter*60) #< minutes to seconds
        self.reset()

    def isIn(self, frame) -> bool:
        if self.isChange(frame):
            self.timeNow = time.time()
            self.inRoom = True
        elif self.timeNow <= time.time()-self.outAfter:
                self.inRoom = False
        return(self.inRoom)

    def setIn(self, value) -> None:
        self.inRoom = value
    
    def reset(self):
        self.timeNow = time.time()
        self.inRoom = None

def run(fps=1, outAfter=5):
    import os
    import sys
    import time
    import json

    currentDir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(currentDir)

    import database
    import compressingJPG as compressingJPG
    import mqttCommunication as communication

    class Main:
        def __init__(self, fps=1):
            self.fps = fps
            with open("../settings.json", "r") as f:
                settings = json.load(f)
            ip = settings["mqtt"]["ip"]
            port = settings["mqtt"]["port"]
            self.db = database.DatabaseClient(ip, port)
            self.decompresor = compressingJPG.Decompresor()

            self.movementDetector = InRoomDetection(outAfter = outAfter, chgThresh = 4000, noiseThresh = 120)

        def _handleMovementDetection(self) -> None:
            image = self.db.get("cameraImage", None)
            if image != None:
                image = self.decompresor.decompress(image)
                isIn = self.movementDetector.isIn(image)
                self.db.isInRoom = isIn
                if not isIn:
                    if isIn == False:
                        com = communication.COM(ip="127.0.0.1")
                        com.connect()
                        com.publish("smartRoom/autoLights/output", "exitRoom")
                        com.disconnect()

                    self.movementDetector.reset()

            else:
                print("No camera image")
                time.sleep(5)

        def run(self):
            while True:
                self._handleMovementDetection()
                time.sleep(1/self.fps)

    movementDetector = Main(fps)
    movementDetector.run()

if __name__ == "__main__":
    run(fps=1, outAfter=5)