import modules.compressing as compressing
import modules.mqttCommunication as comunication
import modules.packetDetector as packet_detector

class cameraDecoder:
    def __init__(self, ip, topic, port=1883, logger=None):
        self.logger = logger
        self.frame = None
        self.topic = topic
        self.client = comunication.COM(ip, port, name="test")
        self.client.subscribe(self.topic)
        self.client.changeOnMessage(self.handle)
        self.client.loop_forever()
        if self.logger != None:
            self.logger.info("[cameraDecoder] connected to mqtt server")

    def handle(self, client, userdata, frame):
        decompressor = compressing.Decompressor()
        packetDetector = packet_detector.Packet_detector()

        topic = frame.topic
        frame = frame.payload.decode()

        if type(frame) != type(None):
            packetDetector.reset(frame)
            frame = packetDetector.getPacket()
            frame = str(frame).replace("\\", "")
            frame = decompressor.loadJsonFrame(frame)
            frame = decompressor.decompress(frame, loadJson=False)
            if type(frame) != type(None):
                self.frame = frame
    
    def read(self):
        return(self.frame)

if __name__ == "__main__":
    mqttCam = cameraDecoder("127.0.0.1", "smartRoom/camera")
    
