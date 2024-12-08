def run():
    import time
    import json
    import sys
    import os

    currentDir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(currentDir)

    import database
    import mqttCommunication as communication

    with open("../settings.json", "r") as f:
        settings = json.load(f)
    ip = settings["mqtt"]["ip"]
    port = settings["mqtt"]["port"]
    db = database.DatabaseClient(ip, port, name="autoLightsTurnOff")

    while True:
        inRoom = db.get("isInRoom", None)
        if inRoom == False:
            com = communication.COM(ip, port)
            com.connect()
            com.publish("smartRoom/generic/output", "lightsOff")
            com.disconnect()
        time.sleep(1)

if __name__ == "__main__":
    run()