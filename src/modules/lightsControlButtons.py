class Buttons:
    """
    Represents a button object that reads input from specified ports.

    Args:
        upPin (int): The GPIO port number for the "up" button.
        downPin (int): The GPIO port number for the "down" button.
        readRate (float, optional): The rate at which the buttons are read in Hz. Defaults to 10.

    Attributes:
        upPin (int): The GPIO port number for the "up" button.
        downPin (int): The GPIO port number for the "down" button.
    Methods:
        readButtons(): Reads the button states and returns the difference between the "up" and "down" buttons.

    """

    def __init__(self, ardu, upPin, downPin):
        """
        Initializes a Button object.

        Args:
            upPin (int): The GPIO port number for the "up" button.
            downPin (int): The GPIO port number for the "down" button.
            readRate (float, optional): The rate at which the buttons are read in Hz. Defaults to 10.
        """

        self.ardu = ardu
        self.upPin = upPin
        self.downPin = downPin

        self.ardu.gpio.pinMode(pin=self.upPin, mode=self.ardu.gpio.INPUT)
        self.ardu.gpio.pinMode(pin=self.downPin, mode=self.ardu.gpio.INPUT)

    def readButtons(self):
        """
        Returns the difference between the "up" and "down" buttons. Returns 0 if the buttons are not ready to be read.
        """

        res = 0
        gpioRes = self.ardu.gpio.digitalRead(self.upPin)
        if gpioRes >= 0:
            res += gpioRes
        else:
            logging.error("Failed to read buttons, ignoring packet")

        gpioRes = self.ardu.gpio.digitalRead(self.downPin)
        if gpioRes >= 0:
            res -= gpioRes
        else:
            logging.error("Failed to read buttons, ignoring packet")

        return(res)
