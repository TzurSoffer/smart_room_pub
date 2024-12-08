import paho.mqtt.client as mqtt
import json
import random

class COM(mqtt.Client):
    def __init__(self, ip, port=1883, name=None, timeoutPeriod = 60, callbackOnMessage=None, subscribeList=[]):
        if name == None:
            name = str(random.randint(0, 1000))

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
                self.messageCallback(data["content"], msgTopic)

            else:
                print("received incorrect packet")
        except Exception as e:
            print(f"received incorrect packet (got error while parsing): {e}")

    def _validatePacket(self, packet):
        if "len" not in packet or "content" not in packet:
            return(False)

        dataLen = int(packet["len"])
        data = str(packet["content"])

        if len(str(data)) != dataLen:
            print(data)
            print(len(str(data)))
            print(dataLen)
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

class MqttMessageRouter(COM):
    def __init__(self, ip, port=1883, name=None, timeoutPeriod = 60, subscribeList=[], routingMap={}, format="STRING"):
        """_summary_

        Args:
            ip (_type_): _description_
            port (int, optional): _description_. Defaults to 1883.
            name (_type_, optional): _description_. Defaults to None.
            timeoutPeriod (int, optional): _description_. Defaults to 60.
            subscribeList (list, optional): list of topic to subscribe initially. Defaults to [].
            routingMap (dict, optional): Callback map for each topic. Defaults to {}.
            format (str, optional): Format of received packet ("STRING", "BYTES", "JSON", "OTHER"). Defaults to "STRING".
        """
        self.routingMap = routingMap #< {"topic1":method, "topic2: method2"}
        self.format = format.upper()
        
        super().__init__(ip=ip, port=port, name=name,
                         timeoutPeriod=timeoutPeriod,
                         callbackOnMessage=self._onMessage,
                         subscribeList=subscribeList)

    def _validatePacket(self, packet):
        if super()._validatePacket(packet) == False:
            return(False)

        if (format == "JSON") and (data.strip()[0] != "{" or data[-1] != "}"):
            return(False)

        return(True)

    def _onMessage(self, client, clientDat, msg) -> None:
        """
        Routes incoming menages based on their topic by routing it to it's corresponding function/callback from the routing map.
        """
        msgPayload = msg.payload.decode("utf-8")
        try:
            data = json.loads(msgPayload)
            
            if "senderId" in data:
                senderId = data["senderId"]
                if senderId == self.name:
                    return()

            if self._validatePacket(data):
                data = data["content"]
                for topic in self.routingMap.keys():
                    if topic == msg.topic:
                        self.routingMap[topic](data)
                        break
                else:
                    print("received incorrect packet")
        except Exception as e:
            print(f"received incorrect packet (got error while parsing): {e}")