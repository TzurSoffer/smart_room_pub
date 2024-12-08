class remotes():
    def __init__(self, sensor, order=[0,1,2,3]):
        self.sensor = sensor
        self.order = order
        
    def isOn(self):
        base = self.sensor.res[ self.order[1] ] == 1 and self.sensor.res[ self.order[3] ] == 1
        if base:
            return(True)
        return(False)
    
    def isOff(self):
        if self.sensor.res[ self.order[0] ] == 1 and self.sensor.res[ self.order[2] ] == 1:
            return(True) 
        return(False)

    def isPassive(self):
        for pin in range(len(self.sensor.res)):
            if self.sensor.res[pin]:
                return(False) #< All pins are zero
        return(True)