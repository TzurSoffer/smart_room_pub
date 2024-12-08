import cv2
import json
import base64
import numpy as np

class Compressor():
    """_summary_
    """
    def __init__(self, shape, keyQuality = 90, deltaQuality  = 80, removeNoise = 0):
        self.matrix_Z1 = np.zeros(shape, dtype=np.uint8)
        self.removeNoise = removeNoise
        self.encode_param_key = [int(cv2.IMWRITE_JPEG_QUALITY), keyQuality]
        self.encode_param_diff = [int(cv2.IMWRITE_JPEG_QUALITY), deltaQuality]

    def _addChannels(self, matrix, channels):
        """_summary_

        Args:
            matrix (_type_): _description_
            chanels (int, optional): _description_. Defaults to 1.
        """
        shape = matrix.shape
        zeros = np.zeros(shape[:2], dtype=np.uint8)
        return(np.dstack((matrix, *[zeros for _ in range(channels)])))

    def _splitPosNeg(self, matrix):
        """_summary_

        Args:
            matrix (_type_): _description_
        """
        pos = np.where(matrix>=0, matrix, 0)    #< anywhere a value in the matrix is smaller than 0 set it to 0
        neg = np.where(matrix<0, matrix, 0)*-1     #< anywhere a value in the matrix is larger than 0 set it to 0
        neg.astype(np.uint8)
        return((pos, neg))

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
        """return a compressed image based on the previus image

        Args:
            matrix (np image): an image you want to compress

        Returns:
            str: json string with the compressed image
        """
        diff = np.subtract(self.matrix_Z1, matrix, dtype=np.int16)
        self.matrix_Z1 = matrix
        
        if self.removeNoise > 0:
            diff = self._removeNoise(diff, thresh=self.removeNoise)  #< remove noise
        pos_neg = self._splitPosNeg(diff)                            #< split neg and pos to different channels
        M = np.dstack(pos_neg)                                       #< Combile into two channels
        M = self._addChannels(M, channels=1)                         #< Add the third channel as zeros
        _, M = cv2.imencode('.jpg', M, self.encode_param_diff)       #< Encode to jpg
        json_str = self._makeJsonFrame(key="delta", binDat=M)        #< embed compressed data into JSON string
        return(json_str)
    
    def compressKey(self, matrix) -> str:
        """compresses a key frame

        Args:
            matrix (np array of image): and image to compress(jpg)

        Returns:
            str: json string of the compressed image
        """
        self.matrix_Z1 = matrix
        M = self._addChannels(matrix, channels=2)                    #< Add second and third channels as zeros
        _, M = cv2.imencode('.jpg', M, self.encode_param_key)        #< Encode to jpg
        json_str = self._makeJsonFrame(key="key", binDat=M)          #< embed compressed data into JSON string
        return(json_str)
    


class Decompressor():
    def __init__(self):
        self.keymatrix = None
    
    def loadJsonFrame(self, json_str):
        frame = json.loads(json_str)
        if "data" in frame:
            frame["data"] = np.array(list(base64.b64decode(frame["data"]))).astype(np.uint8)
        return frame

    def _decompressDelta(self, delta):
        if type(self.keymatrix) != type(None):
            delta = cv2.imdecode(delta, cv2.IMREAD_COLOR).astype(np.int16) #< Decode received delta image
            pos = delta[:,:,1]
            neg = delta[:,:,0]

            self.keymatrix = np.add(self.keymatrix, pos)
            self.keymatrix = np.subtract(self.keymatrix, neg)
            self.keymatrix = np.clip(self.keymatrix, 0, 255)               #< clip error from jpg
            self.keymatrix = self.keymatrix.astype(np.uint8)               #< save as uint8
        
        return(self.keymatrix)
    
    def _decompressKey(self, key):
        key = cv2.imdecode(key, cv2.IMREAD_COLOR) #< Decode received delta image
        self.keymatrix = key[:,:,0]

        return(self.keymatrix)

    def decompress(self, matrix, loadJson=True):
        if loadJson:
            matrix = self.loadJsonFrame(matrix)
        key = matrix["key"]
        if key == "key":
          return(self._decompressKey(matrix["data"]))
        else:
          return(self._decompressDelta(matrix["data"]))
