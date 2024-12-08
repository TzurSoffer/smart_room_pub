import json
import logging as logging

class Packet_detector:
    def __init__(self, sof='{', eof='}', level=logging.INFO):
        logging.basicConfig(level=level)
        self.logger = logging.getLogger()
        self.sof = sof #< Start-Of-Frame character
        self.eof = eof #< End-Of-Frame character
        self.reset()

    def reset(self, buf="") -> None:
        """ Reset the buffer to empty of some init' data """
        self.buf = str(buf)
        self.idxSt = -1

    def update(self, chunk) -> None:
        """ Update the detector with new chunk of data """
        self.buf += chunk
        
    def getPacket(self) -> str:
        """ Returns a complete packet if exists or empty string if not """
        if self.idxSt == -1:
            self.idxSt = self.buf.find(self.sof)  #< Look for start of packet
        idxEnd = self.buf.find(self.eof)          #< Look for end of packet

        pkt = ""
        if self.idxSt >= 0:
            self.logger.debug( "### Start of packet detected" )
            if self.idxSt < idxEnd:
                self.logger.debug( "### Complete of packet detected" )
                pkt = self.buf[self.idxSt:idxEnd+1] #< Get the packet
                pkt = pkt[pkt.rfind('{'):]     #< Trimming for multiple SOF symbols" )
                self.reset( self.buf[idxEnd:] )     #< Remove it and keep the rest
                
            elif idxEnd != -1:
                self.logger.debug( "### Corrupted packet exists at the beginig of the buffer" )
                self.buf = self.buf[self.idxSt:] #< Remove it and keep the rest
                self.idxSt = 0

            else:
                self.logger.debug( "### Incomplete packet at the beginig of the buffer" )
                if self.idxSt > 0:
                    self.logger.debug( "### Removing garbage from the begining" )
                    self.buf = self.buf[self.idxSt:] #< Remove the garbage at the begining
                    self.idxSt = 0
                
        else:
            self.logger.debug( "### Clear the buffer from all garbage" )
            self.reset()

        return(pkt)
        

if __name__ == "__main__":
    def packetSlicer(pkt, sliceSize) -> list:
        l = []
        i = 0
        pktEnd = len(pkt)
        while i < pktEnd:
            end = i +sliceSize
            if end > pktEnd:
                end = pktEnd
            l.append( pkt[i:end] )
            i += sliceSize
        return l

    tx_json_str = json.dumps({"KEY":"key", "dat":"1234a34b83464AF=="})

    rx_noise_pre = "12}!2{/" #< Some noise to add after the "real" packet
    #rx_noise_pre = "z ds.,/"  #< Some noise to add befor the "real" packet
    rx_noise_post = "123!2,/" #< Some noise to add after the "real" packet
    rx_noise_post1 = "12}!2,/" #< Some noise to add after the "real" packet

    rx_pkt = tx_json_str +rx_noise_pre +tx_json_str +rx_noise_post +rx_noise_post1

    print(rx_pkt)
    rx_packets = packetSlicer(rx_pkt, 5)

    pktDetector = Packet_detector()
    for i, pkt in enumerate(rx_packets):
        print( "\n%d. received packet: %s"%(i, pkt) )
        pktDetector.update(pkt)
        print( pktDetector.getPacket() )