###       TODO       ###
#
#
#
#

import threading
import time as time
import json as json
import os
import sys
import subprocess
import logging
import modules.lightsControlButtons as lightsControlButtons
import modules.scheduler as scheduler
from GSOF_ArduBridge import ArduBridge
from modules import timer
from modules import lights
from modules import buildCommand
from modules import infoHandler
from modules import mqttLogger
from modules import remoteArdu
from modules import arduinoVersionControl

from modules import mqttCommunication as communication

class Room():
    def __init__(self, inputTopics=["smartRoom/arduino/input"]):
        self.inputTopics = inputTopics
        self._init()

    def _init(self):
        self.basedir = os.getcwd()+"/"
        self.features = self._getFeatures()
        self.activeFeatures = self._getActiveFeatures()
        with open(self.basedir+"settings.json", "r") as f:
            self.settings = json.load(f)
            self.mqttSettings = self.settings["mqtt"]
            self.loggerSettings = self.settings["loggerSettings"]
            self.coreSettings = self.settings["coreSettings"]
            self.lightSettings = self.features["lights"]
            self.lightButtonsSettings = self.features["lightButtons"]

        logLevels = { 'CRITICAL': logging.CRITICAL, 'ERROR': logging.ERROR, 'WARNING': logging.WARNING, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'NOTSET': logging.NOTSET }
        self.logger = self._initLogger(logLevels[self.loggerSettings["logLevel"].upper()])
        self.run = False
        
        self.ip = self.mqttSettings["ip"]
        self.port = self.mqttSettings["port"]
        self.com = communication.COM(self.ip, self.port, name="smartRoomCore")
        self.startListener()

        self.maxFPS = self.coreSettings["maxAppFPS"]
        self.maxSleepTime = 1/self.maxFPS

        self.maxArduIOSpeed = self.coreSettings["maxArduIOSpeed"]
        self.maxArduIOSleepTime = 1/self.maxArduIOSpeed

        # python -c "import serial.tools.list_ports; [print(f'Port: {port.device}, Description: {port.description}, HWID: {port.hwid}') for port in serial.tools.list_ports.comports()]"
        self.ardu = self._initArdu(self.coreSettings["arduComport"], baudRate = 115200*2, logger=self.logger)   #< "/dev/ttyACM0"
        self.processTimer = timer.Timer()
        self.sensorTimer = timer.Timer()
        self.arduScheduler = scheduler.CommandScheduler(logger=self.logger)

        # create the version control control object
        self.versionControl = arduinoVersionControl.VersionControl(self.arduScheduler, self.ardu)

        # create the light control object
        self.lightsStep = 4               #< in percent
        self.lights = lights.ServoLights(self.arduScheduler,
                                         self.lightSettings["arduPin"],
                                         self.ardu,
                                         reverse=self.lightSettings["reverse"],
                                         zeroAt=self.lightSettings["zeroAt"],
                                         floor=self.lightSettings["min"],
                                         ceil=self.lightSettings["max"])

        # create the buttons light controller object
        self.lightButtonController = lightsControlButtons.Buttons(self.ardu,
                                         upPin=self.lightButtonsSettings["onPin"],
                                         downPin=self.lightButtonsSettings["offPin"]
                                         )

        # create and start all the sensors
        self.remoteArduPins = [12, 13, 8, 9]

        # create infoSender object
        self.infoSender = infoHandler.handlerMQTT(data={"lightSwitchLevel": self.lights.getPercent})

        # create remoteArdu object
        self.remoteArdu = remoteArdu.RemoteArdu(self.ip, self.port, self.arduScheduler, self.ardu, logger=self.logger)

    def _initLogger(self, logLevel=10):
        self.activeLoggers = self.loggerSettings["handlers"]
        
        # create logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logLevel)

        # Create a file handler
        fileHandler = logging.FileHandler('roomLog.log')
        fileHandler.setLevel(logLevel)

        # Create a terminal handler
        terminalHandler = logging.StreamHandler()
        terminalHandler.setLevel(logLevel)

        # Create a mqtt handler

        mqttHandler = mqttLogger.MQTTHandler()
        mqttHandler.setLevel(logLevel)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

        # Set the formatter for the handlers
        fileHandler.setFormatter(formatter)
        terminalHandler.setFormatter(formatter)
        mqttHandler.setFormatter(formatter)

        # Add the handlers to the logger
        if self.activeLoggers["file"]:
            logger.addHandler(fileHandler)
        if self.activeLoggers["console"]:
            logger.addHandler(terminalHandler)
        if self.activeLoggers["mqtt"]:
            logger.addHandler(mqttHandler)
        return(logger)

    def getSensorName(self, topic):
        return(topic.split("/")[-1])

    def startListener(self):
        self.com.connect()
        for topic in self.inputTopics:
            self.com.subscribe(topic)
        self.com.changeOnPacket(self._onPacket)
        self.com.loop_start()

    def _onPacket(self, data, topic):
        dataList = data.split(" ")
        if len(dataList) == 2:
            if dataList[0] == "lightsSet":
                try:
                    self.lights.move(int(dataList[1]))
                except:
                    self.logger.warning("Can't set lights because position is not a valid number")

        elif data == "lightsOn":
            self.lights.move(100)

        elif data == "lightsOff":
            self.lights.move(0)

        elif data == "lightsToggle":
            lightsPercent = self.lights.getPercent()
            if lightsPercent == 0:         #< decide whether to turn on or off the lights
                self.lights.move(80)
            else:
                self.lights.move(0)

        elif data == "lightsUp":
            self.lights.step(dc = self.lightsStep)

        elif data == "lightsDown":
            self.lights.step(dc = -self.lightsStep)

    def _getAndLogTime(self, func, args=(), maxTime=0.04):
        b = time.time()
        res = func(*args)
        runtime = round(time.time()-b, 5)
        if runtime >= maxTime:
            self.logger.warning(f"Function {func.__name__} took an abnormal amount of time to finish: {runtime}")
        return(res, runtime)

    def _lightButtonControlSensor_thread(self, rate=10):
        self.lightButtonControlSensor = buildCommand.Sensor(name="lightButtons", func=self.lightButtonController.readButtons, args=[], initVal=0)
        sleepTime = 1/rate
        while self.run:
            self.arduScheduler.push(self.lightButtonControlSensor)
            time.sleep(sleepTime)
    #         print(f"{sensor.name}: {round(sensor.readTime, 5)}")

    def readRemote(self) -> list:
        """ return all the remote pin values in order """
        val = [0]*len(self.remoteArduPins)
        for i, pin in enumerate(self.remoteArduPins):
            # b = time.time()
            val[i] = self.ardu.gpio.digitalRead(pin)
            # self.logger.debug(f"{i}: {time.time()-b}")
        return(val)

    def _initArdu(self, port, baudRate = 115200*2, logger=None) -> ArduBridge:
        self.logger.info('[smart room] Using port %s at %d'%(port, baudRate))
        ardu = ArduBridge.ArduBridge(COM=port, baud=baudRate, RxTimeOut=0.1, logger=logger) #< The GSOF_arduBridge core object

        self.logger.info('[smart room] Discovering ArduBridge on port %s'%(port))

        if ardu.OpenClosePort(1):
            self.logger.info(f"[smart room] ArduBridge {port} is ON-LINE.")
        else:
            self.logger.error(f"[smart room] ArduBridge {port} is OFF-LINE.")
            ardu = None

        return(ardu)

    def start(self) -> None:
        """ Start the main thread (process) """
        try:
            self.logger.info("[smart room] smart room is starting")

            self.run = True

            # load active features
            self.arduScheduler.start()
            self.activeFeatures = self._getActiveFeatures()

            # start the main program
            if self.activeFeatures["lightButtons"]:
                threading.Thread(target=self._lightButtonControlSensor_thread, args=(self.lightButtonsSettings["readFrequency"],)).start()
            threading.Thread(target=self.process).start()

            # start the infoSender
            self.infoSender.start()

            # start the remoteArdu
            self.remoteArdu.start()

            firmwareVersion = self.versionControl.getVersion().rstrip().removesuffix("\n")
            targetVersion = self.coreSettings["arduFirmware"].removesuffix(".hex").split("/")[-1]
            print(targetVersion)
            print(firmwareVersion)

            if (targetVersion != firmwareVersion) and self.coreSettings["arduFirmwareNoPromptUpdate"] == True:
                self.logger.warning("Firmawre version is not the one wanted by the smart-room, updating...")
                self.updateFirmware()
                return()

            message = "[smart room] smart room has successfully started"
            self.logger.info(message)

        except Exception as e:
            self.logger.error(f"[smart room] smart room has failed to start with error: {e}")

    def stop(self) -> None:
        """ Stop the main thread (process) """
        # stop the main program
        self.run = False

        # stop the arduino scheduler
        self.arduScheduler.stop()

        # stop the infoSender
        self.infoSender.stop()

        # stop the remoteArdu
        self.remoteArdu.stop()

        # stop mqttLisener
        self.com.loop_stop()

        message = "[smart room] smart room has successfully stopped"
        self.logger.info(message)

    def restartApp(self):
        """Restarts the current program."""
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit()

    def updateFirmware(self) -> None:
        self.stop()
        self.versionControl.updateFirmware(self.coreSettings["arduFirmware"])
        self.restartApp()

    def changeSetting(self, setting, val) -> None:
        """ changes a setting value and save the new setting file """
        settings = self._getSettings()
        settings[setting]["status"] = val
        with open(self.basedir+"settings.json", "w") as f:
            json.dump(settings, f)

    def _getSettings(self) -> dict:
        """ loads the settings file """
        with open(self.basedir+"settings.json", "r") as f:
            settings = json.load(f)
        return(settings)

    def _getFeatures(self) -> dict:
        """ get the "features" section of the settings file """
        settings = self._getSettings()
        return(settings["features"])

    def _getActiveFeatures(self) -> dict:
        """ returns all of the features and its state as a dict"""
        activeFeatures = {}
        features = self._getFeatures()
        featureKeys = list(features.keys()) #< get all the features
        for key in featureKeys:
            active = features[key]["active"]
            activeFeatures[key] = active
        return(activeFeatures)

    def _handleInfoSender(self):
        self.infoSender.run = self.activeFeatures["infoSender"]

    def _handleLightsButtonControl(self) -> None:
        try:
            direction = self.lightButtonControlSensor.res #< -1 for bottom button, 1 for top button, and 0 for passive
        except:
            return()
        if direction != 0:
            self.lights.step(dc=int(direction*self.lightsStep))

    def process(self):
        while self.run:
            b = time.time()

            self.features = self._getFeatures()
            self.activeFeatures = self._getActiveFeatures()

            _, handleInfoSenderTime = self._getAndLogTime(self._handleInfoSender)

            if self.activeFeatures["lights"]:
                if self.processTimer.isTimeUp(self.maxArduIOSleepTime):
                    self.processTimer.reset()
                    _, handleLightsButtonControlTime = self._getAndLogTime(self._handleLightsButtonControl)

            time.sleep(max(self.maxSleepTime-(time.time()-b), 0))

if __name__ == "__main__":
    print("RUNNING VERSION 2.1.1")
    room = Room()
    try:
        room.start()

    except KeyboardInterrupt:
        print("[smart room] existing program gracefully\n[smart room] existing program gracefully")
        room.logger.info("[smart room] existing program gracefully")
        room.stop()

    except Exception as e:
        room.logger.critical(f"[smart room] unexpected error: {str(e)}")
        room.stop()
