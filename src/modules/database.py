import threading
import time
import sys
import os

currentDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currentDir)

import mqttCommunication as communication

class MqttDatabase:
    def __init__(self, ip, port=1883, topic="smartRoom/database", name=None, updateEvery=15):
        self._data = {}
        self.topic = topic
        self.com = communication.COM(ip, port, name=name)
        threading.Thread(target=self.updateEvery, args=(updateEvery,), daemon=True).start()

        self.startListener()

    def updateEvery(self, every=15):
        while True:
            for data in self._data:
                self.publishData(data, {"ret": True, "data": self._data[data]})
            time.sleep(every)

    def startListener(self):
        self.com.connect()
        self.com.subscribe(f"{self.topic}/input")
        self.com.subscribe(f"{self.topic}/getData")
        self.com.changeOnPacket(self._onPacket)
        self.com.loop_forever()

    def publishData(self, key, data):
        self.com.publish(f"{self.topic}/{key}", data)

    def _onPacket(self, data, topic):
        if topic == f"{self.topic}/getData":
            if data in self._data:
                self.publishData(data, {"ret": True, "data": self._data[data]})
            else:
                self.publishData(data, {"ret": False, "data": None})
        elif topic == f"{self.topic}/input":
            # print(f"setData {list(data.keys())[0]}")
            self.setVariable(list(data.keys())[0], list(data.values())[0])

    def setVariable(self, key, value):
        self._data[key] = value
        self.publishData(key, {"ret": True, "data": self._data[key]})

    def close(self):
        self.com.loop_stop()
        self.com.disconnect()

class DatabaseClient:
    def __init__(self, ip, port=1883, topic="smartRoom/database", name=None, onChange=None):
        super().__setattr__('_data', {})
        super().__setattr__('_waitingFor', {})
        super().__setattr__('subscribers', [])
        super().__setattr__('topic', topic)
        super().__setattr__('com', communication.COM(ip, port, name=name))
        super().__setattr__('onChange', onChange)

        self.startListener()

    def startListener(self):
        self.com.connect()
        self.com.changeOnPacket(self._onPacket)
        self.com.loop_start()

    def getData(self, key):
        self.com.publish(f"{self.topic}/getData", key)
        timeout = 2
        b = time.time()
        self._waitingFor[key] = True
        while time.time() - b < timeout:
            if (self._waitingFor[key] == False) and (key in self._data):
                # print(f"GetData got {self._data[key]}")
                return(True, self._data[key])
        # print(f"Didn't hear back from server within {timeout} seconds.")
        return(False, None)

    def set(self, key, value):
        if (key not in self._data) or (self._data[key] != value):
            self.com.publish(f"{self.topic}/input", {key: value})
        topic = f"{self.topic}/{key}"
        self.subscribe(topic)
        self.getData(key)

    def changeOnVariableUpdate(self, onChange):
        super().__setattr__('onChange', onChange)

    def _onPacket(self, data, topic):
        key = topic.split("/")[-1]
        if data["ret"]:
            self._data[key] = data["data"]
            self._waitingFor[key] = False
            if self.onChange != None:
                self.onChange(key, data["data"])
        # print(f"Received message from {topic}: {self._data.get(key, 'No Data')}")

    def _getData(self, key):
        if key in self._data:
            return(self._data[key])
        else:
            topic = f"{self.topic}/{key}"
            if topic not in self.subscribers:
                self.subscribe(topic)
                data = self.getData(key)
                if data[0]:
                    return(data[1])
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __getattr__(self, key):
        return(self._getData(key))

    def get(self, key, default=None):
        try:
            return(self._getData(key))
        except:
            return(default)

    def __setattr__(self, key, value):
        self.set(key, value)

    def setInternal(self, key, value):
        super().__setattr__(key, value)

    def subscribe(self, topic):
        if topic not in self.subscribers:
            self.com.subscribe(topic)
            self.subscribers.append(topic)

    def close(self):
        self.com.loop_stop()
        self.com.disconnect()

if __name__ == "__main__":
    # db = MqttDatabase("127.0.0.1", updateEvery=15)
    db = DatabaseClient("127.0.0.1")
