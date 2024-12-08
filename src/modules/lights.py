import time
import modules.buildCommand as buildCommand
import threading

class ServoLights():
    def __init__(self, scheduler, pwm, ardu, reverse=False, zeroAt=50, floor=0, ceil=100):
        self.ardu = ardu
        self.scheduler = scheduler
        self.pwm = pwm
        self.pos = 0
        self.percent = 0
        self.reverse = reverse
        self.range = 255
        self.zeroAt = zeroAt
        self.floor = self.range*(floor/100)
        self.ceil = self.range*(ceil/100)
        self.zeroAtPosition = self.range*(zeroAt/100)

        self.scheduler.push(buildCommand.Command(self.ardu.gpio.pinMode, (self.pwm, 2)))

    def _clip(self, val, minimum=0, maximum=100):
        return(min(max(val, minimum), maximum))
    
    def _shrinkPos(self, pos):                                       #< shrink the percentage so it fits between the floor and the ceil
        return(pos*((self.ceil-self.floor)/self.range)+self.floor)

    def percentToPosition(self, percent):
        if percent <= 0:
            if self.reverse:
                return(self.range-self.floor)
            return(self.floor)

        pos = (self._clip(percent, minimum=0, maximum=100)/100)*(self.range-self.zeroAtPosition)+(self.zeroAtPosition)
        pos = int(self._shrinkPos(pos))
        if self.reverse:
            pos = self.range-pos
        return(pos)

    def positionToPercent(self, position):
        percent = (self._clip(position-self.zeroAtPosition, minimum=0, maximum=self.range-self.zeroAtPosition)/(self.range-self.zeroAtPosition))*100
        if self.reverse:
            percent = 100-percent
        return(percent)

    def _moveToPosition(self, pos):
        pos = int(pos)
        self.scheduler.push(buildCommand.Command(self.ardu.gpio.servoWrite, (self.pwm, pos)))
        self.pos = pos
        return(self.pos)
    
    def move(self, percent):
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        self.percent = percent

        return(self._moveToPosition(self.percentToPosition(percent)))

    def step(self, dc=10):
        self.move(self.percent+dc)

    def getPos(self):
        return(self.pos)
    
    def getPercent(self):
        return(self.percent)