import time
import numpy as np
from PIL import Image

import os
import sys

currentDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currentDir)

import database
import mqttCamera

class AudioHandler:
    def __init__(self, audioObject=None, ip="127.0.0.1", port=1883, topic="audio"):
        self.audioObject = audioObject
        self.ip = ip
        self.port = port
        self.topic = topic
        self.imageCom = None
        self.db = database.DatabaseClient(self.ip, self.port, name="audioSender")

    def audioBufferToImage(self, buffer, width=800, height=200, color=(255, 0, 0), background=(0, 0, 0)):
        """
        Convert the audio buffer to a raw image.

        Args:
        - width (int): Width of the image.
        - height (int): Height of the image.
        - color (tuple): Color of the waveform.
        - background (tuple): Background color of the image.

        Returns:
        - Image: PIL Image object representing the audio waveform.
        """
        if len(buffer) == 0:
            return(None)

        # Combine the audio data from the buffer into a single array
        audioData = np.concatenate(buffer)

        # Normalize the audio data
        audioData = audioData / 15_000
        audioData = np.clip((audioData + 1) / 2, 0, 1)  # Normalize to range [0, 1]

        # Create an empty image
        image = Image.new("RGB", (width, height), background)
        pixels = image.load()

        # Draw the waveform
        for x in range(width):
            index = int(x / width * len(audioData))
            value = int(audioData[index] * height)
            for y in range(height - value, height):
                pixels[x, y] = color

        return(np.array(image))

    def sendAudioData(self, buffer=None, asImage=False):
        if buffer == None:
            buffer = self.audioObject.audioBuffer
        if asImage == True:
            image = self.audioBufferToImage(buffer)
            try:
                if self.imageCom == None:
                    self.imageCom = mqttCamera.MqttCamera(image.shape, ip=self.ip, port=self.port, topic=f"{self.topic}Image", compressor="JPG")
                self.imageCom.sendFrame(image)
            except Exception as e:
                time.sleep(1)
                return()
        else:
            self.db.set(f"{self.topic}Data", buffer)

def run(fps=20, inputDeviceIndex="USB Audio Device"):
    import json
    import os
    import sys

    currentDir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(currentDir)
    import audioReader

    class Main:
        def __init__(self, fps, inputDeviceIndex) -> None:
            with open("../settings.json", "r") as f:
                settings = json.load(f)
            ip = settings["mqtt"]["ip"]
            port = settings["mqtt"]["port"]

            self.fps = fps

            self.audioReader = audioReader.Reader(inputDeviceIndex=inputDeviceIndex, bufferLength=2048)
            self.audioSender = AudioHandler(ip=ip, port=port)

            self.audioReader.printDeviceInfo()
            self.audioReader.initAudio()

        def _getAudioData(self):
            data = self.audioReader.getAudio()
            return(data)

        def _handleAudioSender(self):
            data = self._getAudioData()
            self.audioSender.sendAudioData(buffer=data.tolist(), asImage=False)
        
        def run(self):
            while True:
                self._handleAudioSender()
                time.sleep(1/self.fps)
    
    sender = Main(fps, inputDeviceIndex)
    sender.run()

if __name__ == "__main__":
    run()