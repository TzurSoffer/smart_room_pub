import json
import random
import paho.mqtt.client as mqtt

class COM(mqtt.Client):
    def __init__(self, ip, port=1883, name=None, timeoutPeriod = 60, callbackOnMessage=None, subscribeList=[]):
        if name == None:
            name = str(random.randint(0, 1000))
            super().__init__()
        else:
            super().__init__(name)
        self.messageCallback = print
        self.name = name
        self.ip = ip
        self.port = port
        self.timeoutPeriod = timeoutPeriod
        if callbackOnMessage == None:
            callbackOnMessage = self._onMessage
        self.callbackOnMessage = callbackOnMessage
        self.subscribeList = subscribeList

    def _onMessage(self, client, clientDat, msg) -> None:
        """
        Routes incoming menages based on their topic by routing it to it's corresponding function/callback from the routing map.
        """
        msgPayload = msg.payload.decode("utf-8")
        msgTopic = msg.topic
        try:
            data = json.loads(msgPayload)

            if "senderId" in data:
                senderId = data["senderId"]
                if senderId == self.name and senderId != "":
                    return()

            if self._validatePacket(data):
                if "content" in data:
                    data = data["content"]
                    self.messageCallback(data, msgTopic)
                else:
                    print("no content key in data")

            else:
                print("received incorrect packet")
        except Exception as e:
            print(f"received incorrect packet (got error while parsing): {e}")

    def _validatePacket(self, packet):
        if "len" not in packet or "content" not in packet:
            return(False)

        dataLen = int(packet["len"])
        data = str(packet["content"])

        if len(data) != dataLen:
            return(False)

        return(True)

    def _connect(self) -> None:
        try:
            if super().connect(self.ip, self.port, self.timeoutPeriod) != 0:
                raise Exception("[MQTT] Connection refused")
        except Exception as e:
            raise Exception(f"[MQTT] Could not connect to mqtt broker, wrong ip or port?\n{e}")

    def subscribe(self, topic, qos=0):
        super().subscribe(topic, qos)

    def connect(self, qos=0) -> None:
        self._connect()
        if self.callbackOnMessage != None:
            self.changeOnMessage(self.callbackOnMessage)
        for sub in self.subscribeList:
            self.subscribe(sub, qos=qos)                             #< Call subscribe() for every item in subscribeList 

    def publish(self, topic, msg):
        msg = {"senderId": self.name, "len": len(str(msg)), "content": msg}
        msg = json.dumps(msg)

        super().publish(topic, msg)

    def publishRaw(self, topic, msg):
        super().publish(topic, msg)

    def changeOnMessage(self, onMessage):
        """ changes the on_message function """
        self.on_message = onMessage

    def changeOnPacket(self, onPacket):
        """ changes the on_message function callback after the validationProcess """
        self.messageCallback = onPacket
