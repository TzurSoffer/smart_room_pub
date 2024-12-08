import sys
import os
import copy
import ast

currentDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currentDir)

import mqttCommunication as communication
import database
import buildCommand

class RemoteArdu:
    def __init__(self, ip, port, scheduler, ardu, logger=None):
        self.ip = ip
        self.port = port
        self.scheduler = scheduler
        self.ardu = ardu
        self.logger = logger

        try:
            self.db = database.DatabaseClient(self.ip, self.port, name="remoteArduDB")
            self.db.arduPinValues = {str(i+1): 0 for i in range(13)}
        except:
            if self.logger != None:
                self.logger.error("Database unable to initialize, no result will be returned from digitalRead")
            self.db = None

    def start(self):
        self.com = communication.COM(self.ip, self.port, name="remoteArduCOM")
        self.com.changeOnPacket(self._onPacket)
        self.com.connect()
        self.com.subscribe("smartRoom/remoteArdu/input")
        self.com.loop_start()

    def stop(self):
        self.com.loop_stop()
        self.com.disconnect()

    def _onPacket(self, msg, topic):
        data = msg.split(" ")
        command = data.pop(0)
        if command == "pinMode":
            if len(data) == 2:
                try:
                    command = buildCommand.Command(func=self.pinMode, args=[int(data[0]), int(data[1])])
                    self.scheduler.push(command)
                except:
                    if self.logger:
                        self.logger.error("Data is not an intager")

        elif command == "digitalWrite":
            if len(data) == 2:
                try:
                    command = buildCommand.Command(func=self.digitalWrite, args=[int(data[0]), int(data[1])])
                    self.scheduler.push(command)
                except:
                    if self.logger:
                        self.logger.error("Data is not an intager")

        elif command == "digitalRead":
            if len(data) == 1:
                try:
                    command = buildCommand.Command(func=self.digitalRead, args=[int(data[0])])
                    self.scheduler.push(command)
                except:
                    if self.logger:
                        self.logger.error("Data is not an intager")

        elif command == "wsSetConfig":
            if len(data) == 3:
                try:
                    command = buildCommand.Command(func=self.wsSetConfig, args=[int(data[0]), int(data[1]), ast.literal_eval(data[2])])
                    self.scheduler.push(command)
                except:
                    if self.logger:
                        self.logger.error("Args are not correct")

        elif command == "wsLedWrite":
            if len(data) == 1:
                try:
                    command = buildCommand.Command(func=self.wsLedWrite, args=[ast.literal_eval(data[0])])
                    self.scheduler.push(command)
                except:
                    if self.logger:
                        self.logger.error("Args are not correct")

    def digitalRead(self, pin):
        try:
            pinRes = self.ardu.gpio.digitalRead(pin)
            print(f"pinRes: {pinRes}")
            if self.db != None:
                pinValues = copy.deepcopy(self.db.arduPinValues)
                pinValues[str(pin)] = pinRes
                self.db.arduPinValues = pinValues
        except:
            if self.logger:
                self.logger.error("Failed to update the database with the result.")

    def digitalWrite(self, pin, value):
        self.ardu.gpio.digitalWrite(pin, value)

    def wsSetConfig(self, pin, ledCount, rgb):
        self.ardu.ws.setConfig(pin=pin, leds=ledCount, red=rgb[0], green=rgb[1], blue=rgb[2]) #< 10 LEDs OFF"

    def wsLedWrite(self, leds):
        self.ardu.ws.ledWrite(leds)

    def pinMode(self, pin, mode):
        self.ardu.gpio.pinMode(pin, mode)