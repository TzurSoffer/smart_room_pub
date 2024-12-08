import cv2
import json
import base64
import numpy as np

class Compressor():
    """_summary_
    """
    def __init__(self, shape, keyQuality = 90, deltaQuality  = 80, removeNoise = 0):
        self.removeNoise = removeNoise
        self.encode_param_key = [int(cv2.IMWRITE_JPEG_QUALITY), keyQuality]

    def _addChannels(self, matrix=None, channels=None):
        pass

    def _splitPosNeg(self, matrix=None):
        pass

    def _removeNoise(self, matrix, thresh=3, start=0, delete=False): #< 7 is good for thresh
        if delete == False:
            matrix[np.where(((matrix > start-thresh)&(matrix < start+thresh)))] = start
        else:
            matrix = np.delete(matrix, np.where(((matrix > start-thresh)&(matrix < start+thresh))))
        return(matrix)

    def _makeJsonFrame(self, key, binDat):
        frame = {"key":str(key), "data":(base64.b64encode(binDat)).decode("ascii")}
        return json.dumps(frame)

    def compressDelta(self, matrix) -> str:
        return(self.compressKey(matrix))

    def compressKey(self, matrix) -> str:
        """compresses a key frame

        Args:
            matrix (np array of image): and image to compress(jpg)

        Returns:
            str: json string of the compressed image
        """
        self.matrix_Z1 = matrix
        _, matrix = cv2.imencode('.jpg', matrix, self.encode_param_key)        #< Encode to jpg
        json_str = self._makeJsonFrame(key="key", binDat=matrix)          #< embed compressed data into JSON string
        return(json_str)

class Decompresor():
    def loadJsonFrame(self, json_str):
        frame = json.loads(json_str)
        if "data" in frame:
            frame["data"] = np.array(list(base64.b64decode(frame["data"]))).astype(np.uint8)
        return(frame)

    def _decompressDelta(self, delta=None):
        raise Exception("does not exist")
    
    def _decompressKey(self, key):
        key = cv2.imdecode(key, cv2.IMREAD_COLOR) #< Decode received delta image
        return(key)

    def decompress(self, matrix, loadJson=True):
        if loadJson:
            matrix = self.loadJsonFrame(matrix)
        key = matrix["key"]
        if key == "key":
            return(self._decompressKey(matrix["data"]))
        else:
            pass