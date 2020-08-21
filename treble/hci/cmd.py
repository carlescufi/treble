# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

from asyncio import Event
from dataclasses import dataclass, field
import enum
import struct
from typing import Any
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

    def __init__(self, cmd_cls = None, **kwargs):
        if cmd_cls:
            # Downstream command creation
            assert not kwargs.get('data')
            assert cmd_cls.ogf <= 0x3F
            assert cmd_cls.ocf <= 0x3FF
            super().__init__(**kwargs)
            self.opcode = (cmd_cls.ogf << 10) | cmd_cls.ocf
            plen = struct.calcsize(getattr(cmd_cls, 'sig', ''))
            self.hdr = HCICmdHdr(self.opcode, plen)
            self.pack(self.hdr)
            self.event = Event()
        else:
            # Upstream command parsing
            assert kwargs.get('data')
            super().__init__(hdr_cls = HCICmdHdr, **kwargs)

    def header_len(self):
        return struct.calcsize(HCICmdHdr.sig)

    def unpack_header(self):
        self.hdr = self.unpack(HCICmdHdr)

    def payload_len(self):
        return self.hdr.plen

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

def f(d: Any = None, c: str = None):
    m = dict()
    if d:
        m['default'] = d
    if c:
        m['metadata'] = {'doc' : c}
    return field(**m)

@cmd(OGF.CTLR_BB)
class Reset:
    '''Reset'''
    ocf = 0x003

@cmd(OGF.INFO_PARAMS)
class ReadLocalVersionInformation:
    '''Read Local Version Information'''
    ocf = 0x001
    @dataclass
    class ReturnParams:
        sig = '<BBHBHH'
        status: int = f(c='Status')
        hci_ver: int = f(c='HCI Version')
        hci_rev: int = f(c='HCI Revision')
        lmp_pal_ver: int = f(c='LMP PAL Version')
        manu_name: int = f(c='Manufacturer Name')
        lmp_pal_subver: int = f(c='LMP PAL Subversion')

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
