import time
id = 1

class Command():
    """ TBD """
    def __init__(self, func, args=[], name="command"):
        global id
        self.func = func
        self.args = args
        self.time = time.time()
        self.readTime = -1
        self.id = id
        id = ((id +1)%1024)
        self.type = "command"
        self.name = name

    def run(self) -> None:
        self.time = time.time()
        self.func(*self.args)
        self.readTime = time.time()-self.time #< How much time passed between readings
        # print(f"{self.name}: {time.time()-self.time}")

class Sensor(Command):
    """ TBD """
    def __init__(self, name, func, args=[], initVal="N/A"):
        super().__init__(func, args, name=name)
        self.res = initVal
        self.period = 0.0
        self.movAvgN = 10
        self.type = "sensor"

    def run(self) -> None:
        self.time = time.time()
        self.res = self.func(*self.args)
        self.readTime = time.time()-self.time #< How much time passed between readings
        self.period = self.movAvg(self.readTime)  #< Update the period time with the moving average value

    def getResult(self):
        return(self.res)

    def movAvg(self, val) -> float:
        """ Returns the approximate moving average value
        Args:
            val (float): The new value
        """
        period = self.period +(val -self.period)/self.movAvgN #< Approximate a moving average filter
        return(period)