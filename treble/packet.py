from dataclasses import dataclass
import struct
import typing
from typing import NamedTuple

@dataclass(init=False, eq=False)
class Packet:

    data : bytearray = None

    def __init__(self, data : bytes = None):
        self.data = bytearray(data) if data else bytearray()

    def unpack(self, cls : Type[NamedTuple]) -> NamedTuple:
        assert cls.sig
        t = struct.unpack(cls.sig, self.data)
        return cls(*t)

    def pack(self, tup : NamedTuple) -> None:
        self.data[:0] = struct.pack(tup.sig, *tuple(tup))

class HCICmdHdr(NamedTuple):
    sig = '<HB'
    opcode : int
    plen : int

class HCIEvtHdr(NamedTuple):
    sig = '<BB'
    code : int
    plen : int

class HCIACLHdr(NamedTuple):
    sig = '<HH'
    handle : int
    dlen : int

@dataclass(init=False, eq=False)
class HCIACLData(Packet):

    hci_hdr : HCIACLHdr = None

    def __init__(self, data = None):
        super().__init__(data)

class HCIEvt(Packet):
    
    header : HCIEvtHdr = None

class HCICmd(Packet):

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
