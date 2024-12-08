###       TODO       ###
# Add cameraBuffer downloading to cameraBuffer module
# 
# 
#

import time
import json
import os
import logging
import threading

import os
import sys

currentDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules")
sys.path.append(currentDir)

import mqttLogger
import database
import mqttCommunication as communication

class Room():
    def __init__(self, refreshSettingsEvery=30, logLevel=logging.INFO):
        # initialize the run variable to False
        self.run = False

        self.initLogger(logLevel=logLevel)

        # get basic settings
        self.basedir = os.getcwd()+"/"
        self.refreshSettingsEvery = refreshSettingsEvery
        self.settings = self._getSettings()
        self.mqttSettings = self.settings["mqtt"]

        self.ip = self.mqttSettings["ip"]
        self.port = self.mqttSettings["port"]
        self.inputTopics = self._getInputTopics()
        threading.Thread(target=self.refreshSettings_thread).start()

        self.com = communication.COM(self.ip, self.port, name="roomManagerRouter")
        self.startListener()

        self.database = database.MqttDatabase(self.ip, self.port, name="database")

        message = "[smart room server] smart room server has started"
        self.logger.info(message)

    def initLogger(self, logLevel):
        # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logLevel)

        # Create a file handler
        fileHandler = logging.FileHandler('roomServerLog.log')
        fileHandler.setLevel(logLevel)

        # Create a terminal handler
        terminalHandler = logging.StreamHandler()
        terminalHandler.setLevel(logLevel)
        
        # Create a mqtt handler
        
        mqttHandler = mqttLogger.MQTTHandler()
        mqttHandler.setLevel(logLevel)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Set the formatter for the handlers
        fileHandler.setFormatter(formatter)
        terminalHandler.setFormatter(formatter)
        mqttHandler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(terminalHandler)
        self.logger.addHandler(mqttHandler)

    def refreshSettings_thread(self):
        while self.run:
            self.settings = self._getSettings()
            time.sleep(self.refreshSettingsEvery)

    def startListener(self):
        self.com.connect()
        for topic in self.inputTopics:
            self.com.subscribe(topic)
        self.com.changeOnPacket(self._onPacket)
        threading.Thread(target=self.com.loop_forever).start()

    def getSensorName(self, topic):
        return(topic.split("/")[-1])

    def processCommand(self, command, replacements):
        commands = self.settings["commands"]
        if command not in commands:
            self.logger.error("The command was not found in the settings.")
            return()
        
        command = commands[command]
        if "command" in command:
            commandAction = command["command"]                       #< get the command that the message wants to perform
            if commandAction == "sendMessage":
                if "topic" in command and "message" in command:      #< check that the necessary keys for the "sendMessage" are in the content
                    topic = command["topic"]
                    message = command["message"]
                    for replacement in replacements:
                        message = message.replace("{val}", str(replacement), 1)

                    for varName, varValue in self.settings["variables"].items():
                        message = message.replace(varName, varValue)

                    self.logger.debug(f"sending message: {message}")
                    
                    self.com.publish(topic, message)
                else:
                    self.logger.error(f'The "topic" and "message" keys must be in the command definition.')

            elif commandAction == "runCommands":
                if "commands" not in command:
                    self.logger.error(f'The "commands" key must be in the command definition.')
                    return()
                if type(command["commands"]) != list and type(command["commands"]) != tuple:
                    self.logger.error(f'The "commands" key must contain a list or tuple of the commands.')
                    return()
                for cmd in command["commands"]:
                    cmdParts = cmd.split(" ")
                    if len(cmdParts) > 1:
                        replacements = cmdParts[1:]
                    self.processCommand(cmdParts[0], replacements)
        else:
            self.logger.error('The "command" key must be in the command definition.')

    def _getSettings(self) -> dict:
        """ loads the settings file """
        with open(self.basedir+"settings.json", "r") as f:
            settings = json.load(f)
        return(settings)

    def _getInputTopics(self):
        settings = self._getSettings()
        topics = list(settings["features"].keys())
        return(topics)

    def _compareKeys(self, key, jsonKey):
        replacements = []
        keyParts = key.split(" ")
        jsonKeyParts = jsonKey.split(" ")
        varNames = tuple(self.settings["variables"].keys())

        if len(keyParts) != len(jsonKeyParts):
            return(False, replacements)

        for i in range(len(keyParts)):
            keyPart = keyParts[i]
            jsonKeyPart = jsonKeyParts[i]
            if (keyPart != jsonKeyPart):
                if (jsonKeyPart != "{val}") and (jsonKeyPart not in varNames):
                    return(False, replacements)
                replacements.append(keyPart)
        return(True, replacements)

    def _onPacket(self, data, topic):
        self.processInput(data, topic)

    def processInput(self, command, commandName):
        # Get the current settings, which include commands and features
        
        features = self.settings["features"]

        # Check if the commandName exists in the features
        if commandName in features:
            feature = features[commandName]                                                #< Retrieve the feature associated with the topic
            if "commands" in feature:                                                #< Check if the feature has associated commands
                featureCommands = feature["commands"]                                #< Retrieve the commands for the feature
                for featureCommand in featureCommands:
                    ret, replacements = self._compareKeys(command, featureCommand)
                    if ret:
                        command = featureCommands[featureCommand]                    #< Get the command associated with the received data
                        self.processCommand(command, replacements)     #< Process the command using the corresponding command settings
                        self.logger.debug(f"Sensor data processed.")             #< Log that the sensor data has been processed
                        return()

            self.logger.error(f"Sensor data could not be correctly processed.")

        else:
            self.logger.error(f"Sensor on {commandName} not found")

    def _getAndLogTime(self, func, args=(), maxTime=0.04):
        b = time.time()
        try:
            res = func(*args)
        except Exception as e:
            self.logger.error(f"Function {func.__name__} has failed to run with error:\n{e}")

        runtime = round(time.time()-b, 5)
        if runtime >= maxTime:
            self.logger.warning(f"Function {func.__name__} took an abnormal amount of time to finish: {runtime}")
        return(res, runtime)

    def stop(self) -> None:
        """ Stop the main thread (process) """
        # stop the main program

        message = "[smart room] smart room has successfully stopped"
        self.logger.info(message)

if __name__ == "__main__":
    print("Room Manager")
    import time
    room = Room(logLevel=logging.DEBUG)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        room.logger.info("[smart room manager] existing program gracefully")
        room.stop()

    except Exception as e:
        room.logger.critical(f"[smart room manager] unexpected error: {str(e)}")
        room.stop()
