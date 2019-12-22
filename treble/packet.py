import struct
import typing

class Fragment:

    def __init__(self, data = None, sig = None, tup = None):
        if data:
            self.unpack(data)
        else:
            pass

        self.sig = None
        self.tups = None

    def unpack(self):
        assert self.sig
        for t in tups:
            struct.unpack(sig, data)

    def pack(self):
        pass
        #struct.pack(sig, ...)

class HCICmdHdr(typing.NamedTuple):
    sig = '<HB'
    opcode : int
    plen : int

    #def __init__(self, plen):
    #    pass

class HCICmd(Fragment):

    def __init__(self, params):
        super().__init__()
        self.hdr = HCICmdHdr(0x1234, struct.calcsize(params.sig))
        self.tup = (hdr, params)
        self.hdr = HCICmdHdr()
        pass

class Reset(typing.NamedTuple):
    ocf = 0x000C

class LESetScanEnable(typing.NamedTuple):
    ocf = 0x000C
    sig = '<BB'
    le_scan_enable: int
    filter_dups: int

class HCIEvt(Fragment):
    pass

class HCIACLData(Fragment):
    pass

if __name__ == "__main__":

    sse = LESetScanEnable(1, 0)
    #cmd = HCICmd(sse)
