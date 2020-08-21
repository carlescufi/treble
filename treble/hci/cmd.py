# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
import enum
import typing
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from ..packet import Packet

cmds = dict()
def cmd(ogf):
    def wrapper(cls):
        cls.ogf = ogf.value
        opcode = (cls.ogf << 10) | cls.ocf
        cls.opcode = opcode
        cmds[opcode] = cls
        return cls
    return wrapper

@dataclass
class HCICmdHdr:
    sig = '<HB'
    opcode : int
    plen : int

class HCICmd(Packet):

    def __init__(self, cls):
        super().__init__()
        assert cls.ogf <= 0x3F
        assert cls.ocf <= 0x3FF
        self.opcode = (cls.ogf << 10) | cls.ocf
        #plen = struct.calcsize(cls.sig) if cls.sig else 0
        plen = 0
        self.hdr = HCICmdHdr(self.opcode, plen)
        self.pack(self.hdr)
        self.event = Event()

    def header_len(self):
        return struct.calcsize(HCICmdHdr.sig)

    def unpack_header(self):
        self.hdr = self.unpack(HCICmdHdr)

    def payload_len(self):
        return self.hdr.plen

    def unpack_header(self):
        self.hdr = self.unpack(HCICmdHdr)


    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event):
        self._event = event

class OGF(enum.Enum):
    LINK_CONTROL = 1
    LINK_POLICY = 2
    CTLR_BB = 3
    INFO_PARAMS = 4
    STATUS_PARAMS = 5
    TESTING_CMDS = 6
    LE_CTLR_CMDS = 8

@cmd(OGF.CTLR_BB)
class Reset:
    ocf = 0x003

@cmd(OGF.INFO_PARAMS)
class ReadLocalVersionInformation:
    ocf = 0x001
    @dataclass
    class ReturnParams:
        sig = '<BBHBHH'
        status: int
        hci_ver: int
        hci_rev: int
        lmp_pal_ver: int
        manu_name: int
        lmp_pal_subver: int

@cmd(OGF.INFO_PARAMS)
class ReadLocalSupportedCommands:
    ocf = 0x001
    @dataclass
    class ReturnParams:
        sig = '<B64s'
        status: int
        commands: bytes

@cmd(OGF.LE_CTLR_CMDS)
@dataclass(eq=False)
class LESetScanEnable:
    ocf = 0x00C
    sig = '<BB'
    le_scan_enable: int
    filter_dups: int
