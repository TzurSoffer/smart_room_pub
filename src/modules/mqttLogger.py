import os
import sys
import logging
currentDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currentDir)

import mqttCommunication as communication

class MQTTHandler(logging.Handler):
    def __init__(self, ip="127.0.0.1", port=1883, topic="smartRoom/logger"):
        super().__init__()
        self.client = communication.COM(ip=ip, port=port, name="logger")
        self.client.connect()
        self.topic = topic

    def emit(self, record):
        logEntry = self.format(record)
        self.client.publish(self.topic, logEntry)