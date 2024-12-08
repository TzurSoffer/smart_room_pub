import time
import json
import datetime
import threading
import cv2
import sys
import os

currentDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currentDir)

import mqttCommunication as communication

HOUR = 3600
MINUTE = 60
SECOND = 1

class BufferHandler:
    """Class responsible for buffering frames and creating videos that remain openable if interrupted."""

    def __init__(self, saveEvery, resWidth, resLength=None, maxBufferTime=24*3600, saveFolder="./", logger=None):
        self.logger=logger
        self.i = 0
        self.totalFrameCount = int(maxBufferTime / saveEvery)
        self.run = False
        self.lock = False
        self.timeBetweenReads = saveEvery
        self.resWidth = resWidth
        self.resLength = resLength or int(resWidth * 0.75)
        self.saveFolder = saveFolder
        self.lastVideoPath = ""
        self.lastFrameTimestamp = time.time()
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.videoObject = None

    def createVideoObject(self):
        """Initializes a new video file to append frames continuously."""
        now = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        self.lastVideoPath = os.path.join(self.saveFolder, f"{now}.avi")

        # Initialize the video writer
        self.videoObject = cv2.VideoWriter(
            self.lastVideoPath, self.fourcc, 20.0, (self.resWidth, self.resLength), isColor=False
        )

        if not self.videoObject.isOpened():                                               #< Verify if VideoWriter is successfully opened
            raise IOError(f"Failed to open VideoWriter with path: {self.lastVideoPath}")
        print(f"Initialized VideoWriter with size: {self.resWidth}x{self.resLength}")

    def start(self):
        """Starts the buffering process."""
        self.run = True
        if not self.videoObject:         #< Ensure the video object is created when start is called
            self.createVideoObject()

    def addFrame(self, frame) -> None:
        """Adds a frame directly to the video file."""

        if time.time()-self.lastFrameTimestamp < self.timeBetweenReads:
            return()

        if not self.run:
            if self.logger != None:
                self.logger.error("[cameraBufferHandler] Program not running")
            return()

        if self.lock:
            if self.logger != None:
                self.logger.warning("[cameraBufferHandler] Program currently in lock, frame not being appended")
            return()

        if not self.videoObject:
            self.createVideoObject()

        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                 #< Convert the frame to grayscale if it's not already

        scaled = cv2.resize(frame, (self.resWidth, self.resLength))         #< Resize the frame to the specified resolution
        self.videoObject.write(scaled)                                      #< Write the frame to the video file
        # print(f"Frame {self.i + 1} written to {self.lastVideoPath}")

        self.lastFrameTimestamp = time.time()                               #< Update timestamp and frame count
        self.i += 1

        # Check if buffer has reached the max frame count and finalize if necessary
        if self.i >= self.totalFrameCount:
            self.download()

    def download(self):
        """Finalizes the current video file and prepares for the next one."""
        self.lock = True
        if self.videoObject:
            self.videoObject.release()                       #< Finalize the current video
            print(f"Finalized video: {self.lastVideoPath}")

        # Reset the frame count and open a new video file
        self.i = 0
        self.videoObject = None
        self.lock = False
        self.createVideoObject()

class BufferUploadHandler(BufferHandler):
    def __init__(self, saveEvery, resWidth, resLength=None, maxBufferTime=24*HOUR, saveFolder="./", topic="smartRoom/cameraStreamUpload", inputTopic="smartRoom/cameraStreamUpload/input", ip="127.0.0.1", port=1883, timeoutPeriod = 120, name="bufferHandler", attemptConnectEvery=5, logger=None):
        super().__init__(saveEvery, resWidth, resLength, maxBufferTime, saveFolder, logger)
        self.topic = topic
        self.inputTopic = inputTopic
        self.logger = logger
        self.run = False
        self.attemptConnectEvery = attemptConnectEvery
        self.client = communication.COM(ip, port=port, name=name, timeoutPeriod=timeoutPeriod)
        self.client.changeOnPacket(self._onPacket)

    def _onPacket(self, packet, topic):
        self.download()
        self.logger.info("[cameraBufferHandler] downloaded buffer")

    def changeOnPacket(self, onPacket):
        self.client.changeOnPacket(onPacket)

    def connect(self):
        while self.run:
            try:
                self.client.connect()
                self.client.subscribe(self.inputTopic)
                if self.logger != None:
                    self.logger.info("[cameraBufferHandler] connected to mqtt broker")
                self.client.loop_forever()

            except:
                time.sleep(self.attemptConnectEvery)

    def start(self):
        self.run = True
        threading.Thread(target=self.connect).start()

def run():
    import logging
    import schedule

    # Get the directory of the current script
    currentDir = os.path.dirname(os.path.abspath(__file__))

    # Add the target directory to the system path
    sys.path.append(currentDir)

    # Now you can import the module
    import database
    import compressingJPG as compressingJPG
    import mqttLogger

    class Main:
        def __init__(self):
            self.logger = self._initLogger()
            self.cameraBufferHandler = BufferUploadHandler(saveEvery=1*SECOND, resWidth=208, resLength=160, maxBufferTime=24*HOUR, saveFolder="../output/", logger=self.logger)     
            self.cameraBufferHandler.changeOnPacket(self._bufferHandlerOnPacket)
            self.cameraBufferHandler.start()
            self.decompresor = compressingJPG.Decompresor()
            with open("../settings.json", "r") as f:
                settings = json.load(f)
            ip = settings["mqtt"]["ip"]
            port = settings["mqtt"]["port"]
            self.db = database.DatabaseClient(ip, port)
            schedule.every().day.at("00:00").do(self.downloadCameraBuffer)

        def _initLogger(self, logLevel=logging.INFO):
            # create logger
            logger = logging.getLogger(__name__)
            logger.setLevel(logLevel)

            # Create a terminal handler
            terminalHandler = logging.StreamHandler()
            terminalHandler.setLevel(logLevel)

            # Create a mqtt handler

            mqttHandler = mqttLogger.MQTTHandler()
            mqttHandler.setLevel(logLevel)

            # Create a formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

            # Set the formatter for the handlers
            terminalHandler.setFormatter(formatter)
            mqttHandler.setFormatter(formatter)

            # Add the handlers to the logger
            logger.addHandler(terminalHandler)
            logger.addHandler(mqttHandler)
            return(logger)

        def removeOldFiles(self, basePath="../output/", deletePrevious=5):
            fileNames = os.listdir(basePath)
            filePaths = [os.path.join(basePath, f) for f in fileNames]
            fileDates = [datetime.datetime.fromtimestamp(os.stat(f).st_mtime) for f in filePaths]
            now = datetime.datetime.today()
            maxDelay = datetime.timedelta(days=deletePrevious)
            i = 0
            for date in fileDates:
                if now-date < maxDelay:   #< files to keep
                    filePaths.pop(i)
                else:
                    i += 1                #< add 1 only if not poping since pop makes i the next value

            for file in filePaths:
                self.logger.info(f"deleting {file}")
                os.remove(file)

        def downloadCameraBuffer(self, basePath="../output/", deleteOld=5):
            self.cameraBufferHandler.download()
            if type(deleteOld) == int:
                self.removeOldFiles(basePath=basePath, deletePrevious=deleteOld)

        def _bufferHandlerOnPacket(self, packet):
            self.downloadCameraBuffer()
            self.logger.info("[cameraBufferHandler] downloaded buffer")

        def run(self):
            while True:
                image = self.db.get("cameraImage", None)
                if image != None:
                    image = self.decompresor.decompress(image)
                    self.cameraBufferHandler.addFrame(image)
                else:
                    time.sleep(5)
                    continue

                schedule.run_pending()
                time.sleep(0.2)

    Main().run()

if __name__ == "__main__":
    run()
