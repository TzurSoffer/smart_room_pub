import sys
import os

# Get the directory of the current script
currentDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currentDir)

import compressing as compressing
import compressingJPG as compressingJPG
import database

class MqttCamera():
    def __init__(self, shape, keyEvery=5, ip="127.0.0.1", port=1883, attemptConnectEvery=5, compressor="kd", topic="cameraImage"):
        self.keyEvery = keyEvery
        self.frameIndex = self.keyEvery                              #< current frame index
        self.topic = topic
        if compressor == "kd":
            self.compressor = compressing.Compressor(shape, keyQuality = 100, deltaQuality  = 80)
        else:
            self.compressor = compressingJPG.Compressor(shape, keyQuality = 100, deltaQuality  = 80)
        self.attemptConnectEvery = attemptConnectEvery
        self.db = database.DatabaseClient(ip, port)

    def _compressFrame(self, frame):
        if self.frameIndex >= self.keyEvery:
            compressedFrame = self.compressor.compressKey(frame)
            self.frameIndex = 0

        else:
            compressedFrame = self.compressor.compressDelta(frame)

        self.frameIndex += 1
        
        return(compressedFrame)
    
    def sendFrame(self, frame):
        try:
            compressedFrame = self._compressFrame(frame)
            self.db.set(self.topic, compressedFrame)
            return(1)
        except:
            return(-1)

def run(fps=24, res=(640, 480)):
    import time
    import json
    import cv2

    cap = cv2.VideoCapture(-1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution: {width}x{height}")

    _, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mqttCamera = MqttCamera(frame.shape, compressor="JPEG")


    with open("../settings.json", "r") as f:
        settings = json.load(f)
        ip = settings["mqtt"]["ip"]
        port = settings["mqtt"]["port"]
    db = database.DatabaseClient(ip, port)
    db.cameraImageFps = fps

    while True:
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mqttCamera.sendFrame(frame)
        time.sleep(1/fps)

if __name__ == "__main__":
    run()
        