import time
import modules.buildCommand as buildCommand
import serial
import subprocess

class VersionControl():
    def __init__(self, scheduler, ardu):
        self.ardu = ardu
        self.scheduler = scheduler

    def getVersion(self) -> str:
        versionSensor = buildCommand.Sensor("getVersion", self.ardu.GetID)
        beginTime = versionSensor.time
        self.scheduler.push(versionSensor)

        b = time.time()
        while time.time()-b < 5:
            if versionSensor.time != beginTime:
                return(versionSensor.getResult())
            time.sleep(0.01)
        return(-1)

    def updateFirmware(self, hexFilePath=None, baudrate=115200):
        com = self.ardu.COM
        ser = serial.Serial(com, baudrate)
        ser.close()

        # Use avrdude to flash the hex file
        command = f"avrdude -v -patmega328p -carduino -P{com} -b{baudrate} -D -Uflash:w:'{hexFilePath}':i"
        result = subprocess.run(command, shell=True)

        # Check if the flashing was successful
        if result.returncode == 0:
            print("Flashing succeeded")
            return 0
        else:
            print("Flashing failed")
            return -1
