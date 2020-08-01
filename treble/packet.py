from dataclasses import dataclass
import struct
import typing
from typing import Type, NamedTuple

@dataclass(init=False, eq=False)
class Packet:

    data : bytearray = None
    idx : int = 0

    def __init__(self, data : bytes = None, copy=False):
        if data:
            self.data = bytearray(data) if copy else data
        else:
            self.data = bytearray()

    def unpack(self, cls : Type[NamedTuple]) -> NamedTuple:
        assert cls.sig
        s = struct.calcsize(cls.sig)
        t = struct.unpack(cls.sig, self.data[self.idx : self.idx + s])
        self.idx += s
        return cls(*t)

    def pack(self, tup : NamedTuple) -> None:
        self.data[:0] = struct.pack(tup.sig, *tuple(tup))

    def unpack_header(self):
        raise NotImplementedError

class HCICmdHeader(NamedTuple):
    sig = '<HB'
    opcode : int
    plen : int

class HCIEvtHeader(NamedTuple):
    sig = '<BB'
    code : int
    plen : int

class HCIACLHeader(NamedTuple):
    sig = '<HH'
    handle : int
    dlen : int

@dataclass(init=False, eq=False)
class HCIACLData(Packet):

    hdr : HCIACLHeader = None

    def __init__(self, data : bytes = None):
        super().__init__(data)

    def unpack_header(self):
            self.hdr = self.unpack(HCIACLHeader)

class HCIEvt(Packet):
    
    hdr : HCIEvtHeader = None

    def __init__(self, data : bytes = None):
        super().__init__(data)

    def unpack_header(self):
            self.hdr = self.unpack(HCIEvtHeader)

class HCICmd(Packet):

    def __init__(self, cls):
        super().__init__()
        assert cls.ogf <= 0x3F
        assert cls.ocf <= 0x3FF
        self.opcode = (cls.ogf << 10) | cls.ocf
        #plen = struct.calcsize(cls.sig) if cls.sig else 0 
        plen = 0
        self.hdr = HCICmdHeader(self.opcode, plen)
        self.pack(self.hdr)

if __name__ == "__main__":

    sse = LESetScanEnable(1, 0)
    #cmd = HCICmd(sse)
