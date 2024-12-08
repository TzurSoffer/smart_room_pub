import time
import threading
from modules import mqttCommunication

class handlerBase():
    def __init__(self, data=None, sendEvery=5):
        self.run = False
        self.sendEvery = sendEvery
        if data == None:
            data = {}
        self.data = data
    
    def sendEvery_thread(self):
        while self.run:
            self.sendData(self.getData())
            time.sleep(self.sendEvery)

    def setInput(self, data):
        self.data = data

    def getData(self):
        data = {}
        for key, callback in self.data.items():
            data[key] = callback()

        return(data)

    def start(self):
        self.run = True
        threading.Thread(target=self.sendEvery_thread).start()

    def stop(self):
        self.run = False

    def sendData(self, data):
        pass

class handlerMQTT(handlerBase):
    def __init__(self, data=None, ip="127.0.0.1", port=1883, inputTopic="smartRoom/infoGet", outputTopic="smartRoom/sensors", sendEvery=1):
        super().__init__(data, sendEvery=sendEvery)
        self.inputTopic = inputTopic
        self.outputTopic = outputTopic
        self.com = mqttCommunication.COM(ip=ip, port=port, name="infoSender")
        self.com.changeOnPacket(self.onPacket)

    def onPacket(self, packet, topic):
        if packet and self.run:
            self.sendData(self.getData())

    def start(self):
        super().start()
        self.com.connect()
        self.com.subscribe(self.inputTopic, qos=0)
        self.com.loop_start()

    def stop(self):
        super().stop()
        self.com.loop_stop()

    def sendData(self, data):
        super().sendData(data)
        for key, value in data.items():
            self.com.publish(f"{self.outputTopic}/{key}", value)