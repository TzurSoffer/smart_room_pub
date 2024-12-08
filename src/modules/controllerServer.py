import json
import time
import threading
import modules.mqttCommunication as communication

class Server:
    def __init__(self, ip, port=1883, timeoutPeriod = 120, name="guiServer", attemptConnectEvery=5, saveCommand=False, logger=None):
        self.run = False
        self.lastCommand = None
        self.logger = logger
        self.saveCommand = saveCommand
        self.attemptConnectEvery = attemptConnectEvery
        self.client = communication.COM(ip, port=port, name=name, timeoutPeriod=timeoutPeriod)

    def connect(self):
        while self.run:
            try:
                self.client.connect()
                break
            except:
                time.sleep(self.attemptConnectEvery)

        self.client.subscribe("smartRoom/GUI")
        self.client.changeOnMessage(self._onMessage)
        if self.logger != None:
            self.logger.info("[GUIserver] connected to mqtt broker")
        self.client.loop_forever()

    def start(self):
        self.run = True
        threading.Thread(target=self.connect).start()

    def stop(self):
        self.run = False
        self.client.disconnect()
    
    def getLastCommand(self):
        lastCommand = self.lastCommand
        self.lastCommand = None
        return(lastCommand)

    def _onMessage(self, client, userdata, data):
        if self.logger != None:
            self.logger.debug(f"[GUIserver] received data from GUI!!! {data.payload.decode()}")
        try:
            # Here you can use the received data as you want.
            data = data.payload.decode().replace("'", '"')
            data = json.loads(data)
            dataLen = int(data["len"])
            data = str(data["data"])
            if len(data) == dataLen:
                if data.strip()[0] == "{" and data[-1] == "}":
                    if self.logger != None:
                        self.logger.error("[GUIserver] this feature is not yet implemented")
                    # with open("status.json", "w") as f:
                    #     json.dump(json.loads(data.replace("'", '"')), f, indent = True)
                else:
                    self.lastCommand = data
                    if self.saveCommand:
                        with open("commands.txt", "w") as f:
                            f.write(data)
            else:
                if self.logger != None:
                    self.logger.error("[GUIserver] packet is invalid or incomplete")

        except json.decoder.JSONDecodeError:
            pass

        except Exception as e:
            if self.logger != None:
                self.logger.error(f"[GUIserver] {e}")

if __name__ == "__main__":
    import json
    import time
    
    with open("../settings.json", "r") as f:
        settings = json.load(f)
    server = Server(settings["mqtt"]["ip"], settings["mqtt"]["port"], saveCommand=True)
    server.start()
    while True:
        time.sleep(10)