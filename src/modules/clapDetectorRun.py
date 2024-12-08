def run(lowcut=2000, highcut=3000):
    import os
    import sys
    import time
    import json
    from clapDetector import ClapDetector

    currentDir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(currentDir)

    import database
    import mqttCommunication as communication

    class Main:
        def __init__(self, topic="smartRoom/clapDetection/output"):
            with open("../settings.json", "r") as f:
                settings = json.load(f)
            self.ip = settings["mqtt"]["ip"]
            self.port = settings["mqtt"]["port"]
            self.db = database.DatabaseClient(self.ip, self.port, name="clapDetectorRun")
            self.db.changeOnVariableUpdate(self._handleClapDetection)
            self.db.get("audioData")

            self.topic = topic

            # create the clapDetector
            self.clapDetector = ClapDetector(inputDevice=None, logger=None, logLevel=10, bufferLength=2048, resetTime=1.0, audioBufferLength=10)
            self.clapDetectorThreshold = 6000
            self.clapDetectorLowcut = lowcut        #<   2000
            self.clapDetectorHighcut = highcut      #<   2500

        def _isDoubleClap(self, pattern):
            return(len(pattern) == 2)

        def _handleClapDetection(self, topic, audioData) -> None:
            if topic == "audioData":
                if (self.db.get("isInRoom", False) == True) and (audioData):
                    clap = self.clapDetector.run(audioData=audioData, thresholdBias=self.clapDetectorThreshold, lowcut=self.clapDetectorLowcut, highcut=self.clapDetectorHighcut)

                    if self._isDoubleClap(clap):
                        com = communication.COM(self.ip, self.port)
                        com.connect()
                        com.publish(self.topic, "doubleClap")
                        com.disconnect()
                        print("Double Clap!")

        def run(self):
            while True:
                time.sleep(10)
                # print("savingAudio")
                # self.clapDetector.saveAudio(folder="./claps", fileName=None)

    clapDetection = Main()
    clapDetection.run()

if __name__ == "__main__":
    run()