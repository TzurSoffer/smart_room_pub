import pyaudio
import numpy as np
import time
from collections import deque

class Reader():
    """
    ClapDetector Class

    This class provides functionality for detecting claps from an audio input stream. It initializes an audio input 
    device, processes the audio to detect claps based on a dynamic threshold, and can identify patterns of claps. 
    Additionally, it can log the detection events and save audio data.

    Attributes:
    -----------
    inputDeviceIndex : int or str
        The ID or name of the audio input device.
    rate : int
        The sample rate of the microphone. If None, it will be determined automatically.
    bufferLength : int
        The length of the audio clip section (buffer) in samples.

    Methods:
    --------
    findID(self, lookfor="USB Audio Device") -> int:
        Finds the ID of the audio input device based on its name.

    initAudio(self) -> None:
        Initializes the audio input stream.

    restartAudio(self) -> None:
        Restarts the audio input stream.

    printDeviceInfo(self) -> None:
        Prints information about available audio devices.

    getAudio(self, audio=-1) -> np.ndarray:
        Continuously retrieves audio data from the input stream.

    """
    def __init__(self, inputDeviceIndex="USB Audio Device",            #< ID or name/name_section of audio Device
                 rate=None,                                            #< Sample rate of microphone (leave None to get dynamically)
                 bufferLength=1024,                                    #< Length of audio clip section(buffer)
                 audioBufferLength=3.1                                 #< length of audio to save in buffer in seconds (for saving audio to file only. not used in calculations)
                 ):
        if type(inputDeviceIndex) == str:
            inputDeviceIndex = self.findID(lookfor=inputDeviceIndex)
        self.inputDeviceIndex = inputDeviceIndex
        self.rate = rate
        self.audioBuffer = []
        self.audioBufferLength = audioBufferLength
        self.bufferLength = bufferLength
        self.audioData = np.array([], dtype=np.int16)

    def findID(self, lookfor="USB Audio Device"):
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numDevices = info.get('deviceCount')
        
        print("finding device")
        for i in range(0, numDevices):
            deviceInfo = str(p.get_device_info_by_host_api_device_index(0, i)["name"])
            if lookfor in deviceInfo:
                print(f"found {lookfor} in index {i}")
                return(i)

        print(f"{lookfor} was not found in available devices.")
        return(-1)

    def initAudio(self):
        self.p = pyaudio.PyAudio()
        input_device_info = self.p.get_device_info_by_index(self.inputDeviceIndex)
        channels = input_device_info.get('maxInputChannels', 1)
        if self.rate == None:
            self.rate = int(input_device_info.get('defaultSampleRate', 44100))

        self.audioBuffer = deque(maxlen=int((self.rate*self.audioBufferLength)/self.bufferLength))

        print(f"Microphone on index {self.inputDeviceIndex} has {channels} channels and operates at a rate of {self.rate}")
        try:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.bufferLength,
                                  input_device_index=self.inputDeviceIndex)
        except:
            raise Exception("Failed to open audio stream perhaps the audio index/name is incorrect?")
        return(self)
        
    def restartAudio(self):
        try:
            self.stop()
        except:
            print("audio stream failed to stop")
        self.initAudio()
        print("successfully restarted audio stream")
        return(self)

    def printDeviceInfo(self) -> None:
        """
        Print information about available audio devices.

        This method retrieves information about audio devices and prints details for each device,
        including its index and name.

        Returns:
        - None
        """
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numDevices = info.get('deviceCount')

        print("Available audio devices:")
        for i in range(0, numDevices):
            deviceInfo = p.get_device_info_by_host_api_device_index(0, i)
            print(f"Device {i}: {deviceInfo['name']}")
    
    def getAudio(self, audio=-1) -> np.ndarray:
        """
        Continuously retrieve audio data from the input stream.

        This method attempts to read audio data from the input stream and returns the data as a NumPy array.
        If a recording error occurs, it waits for one second, prints an error message, resets the audio stream,
        and retries to obtain the audio data.

        Returns:
        - numpy.ndarray: NumPy array containing the retrieved audio data.
        """
        try:
            if type(audio) == int:
                self.audioData = np.frombuffer(self.stream.read(self.bufferLength, exception_on_overflow=False), dtype=np.int16) #< Convert the raw audio data to a NumPy array of 16-bit integers
            else:                                                                                   #< using else to avoid overwrite of self.audioData with -1 if failed to capture audio
                self.audioData = audio
            self.audioBuffer.append(self.audioData)

        except Exception as e:
            time.sleep(.5)
            print(e)
            print("Recording error, resetting stream and trying again")
            self.restartAudio()
        
        finally:
            return(self.audioData)