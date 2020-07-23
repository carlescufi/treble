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
        t = struct.unpack(cls.sig, self.data[idx : idx+s])
        idx += s
        return cls(*t)

    def pack(self, tup : NamedTuple) -> None:
        self.data[:0] = struct.pack(tup.sig, *tuple(tup))

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

    def __init__(self, data = None):
        super().__init__(data)

    def unpack_header():
            self.hdr = self.unpack(HCIACLHeader)

class HCIEvt(Packet):
    
    hdr : HCIEvtHeader = None

    def __init__(self, data = None):
        super().__init__(data)

    def unpack_header():
            self.hdr = self.unpack(HCIEvtHeader)

class HCICmd(Packet):

    def __init__(self, params):
        super().__init__()
        self.hdr = HCICmdHeader(0x1234, struct.calcsize(params.sig))
        self.tup = (hdr, params)
        self.hdr = HCICmdHeader()
        pass

class Reset(typing.NamedTuple):
    ocf = 0x000C

class LESetScanEnable(typing.NamedTuple):
    ocf = 0x000C
    sig = '<BB'
    le_scan_enable: int
    filter_dups: int

if __name__ == "__main__":

    sse = LESetScanEnable(1, 0)
    #cmd = HCICmd(sse)
