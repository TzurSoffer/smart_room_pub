import threading
import time

class AlarmClock():
    def __init__(self) -> None:
        self.alarmTime = None
        self.nextValidCheckTime = 0

    def setTime(self, time):
        self.alarmTime = time

    def setCallback(self, callback, asThread=True):
        self.callbackAsThread = asThread
        self._callback = callback

    def checkAlarm(self):
        if (self.alarmTime != None) and (time.strftime("%H") == str(self.alarmTime[0]) and time.strftime("%M") == str(self.alarmTime[1])) and (time.time() >= self.nextValidCheckTime):
            self.nextValidCheckTime = time.time()+61
            if self.callbackAsThread:
                threading.Thread(target=self._callback).start()
            else:
                self._callback()

    def _callback(self):
        return(True)
def run():
    import json
    import mqttCommunication as communication

    class Main:
        def __init__(self, topic="smartRoom/alarm_clock/output"):
            with open("../settings.json", "r") as f:
                settings = json.load(f)
            ip = settings["mqtt"]["ip"]
            port = settings["mqtt"]["port"]
            alarmTime = settings["features"]["alarm_clock"]["wakeupTime"].split(":")

            self.topic = topic
            self.com = communication.COM(ip, port)
            self.com.connect()
            
            self.alarm = AlarmClock()
            self.alarm.setTime(alarmTime)
            self.alarm.setCallback(self.callback, asThread=False)

        def callback(self):
            self.com.publish(self.topic, "alarmRing")

        def run(self):
            while True:
                self.alarm.checkAlarm()
                time.sleep(1)

    alarm = Main()
    alarm.run()