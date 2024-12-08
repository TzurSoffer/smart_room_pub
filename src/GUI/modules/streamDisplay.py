from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import json
import base64
from io import BytesIO
from PIL import Image as PILImage

from modules.THEME import THEME
import modules.mqttCommunication as communication

class StreamDisplay(Image):
    def __init__(self, ip, port=1883, cameraTopic="smartRoom/database/cameraImage", **kwargs):
        super().__init__(**kwargs)

        try:
            self.com = communication.COM(ip, port)
            self.com.connect()
            self.com.subscribe(cameraTopic)
            self.com.changeOnPacket(self._onPacket)
            self.com.loop_start()
        except:
            pass

        self.orientation = 'vertical'
        self.background_color = THEME["background"]

    def _onPacket(self, msg, topic):
        self.updateStream(msg)

    def updateStream(self, frame):
        """
        Update the image display with the incoming base64-encoded grayscale image and print its pixel values.
        This method is called from a non-GUI thread.
        """
        # Schedule the actual update to run on the main thread
        Clock.schedule_once(lambda dt: self.updateStreamInMainThread(frame))

    def updateStreamInMainThread(self, frame):
        """
        Update the image display with the incoming base64-encoded JPEG image.
        """
        # Decode the base64 string to raw bytes
        img_data = base64.b64decode(json.loads(frame["data"])["data"])
        
        # Use PIL to open the image from the raw bytes
        image = PILImage.open(BytesIO(img_data))       #< image is grayscale

        image = image.convert('L')

        # Convert the image to a format that Kivy can use
        texture = Texture.create(size=image.size, colorfmt='luminance')

        # Load the image data into the texture
        texture.blit_buffer(image.tobytes(), colorfmt='luminance', bufferfmt='ubyte')
        texture.flip_vertical()  # Flip to correct orientation if needed

        # Update the widget texture
        self.texture = texture
        self.canvas.ask_update()

    def stop(self):
        self.com.loop_stop()
        self.com.disconnect()