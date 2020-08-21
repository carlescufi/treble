# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
import struct
import typing

from ..packet import Packet

all = dict()
def evt(cls):
    all[cls.code] = cls
    return cls

@dataclass
class HCIEvtHdr:
    sig = '<BB'
    code : int
    plen : int

class HCIEvt(Packet):

    def __init__(self, **kwargs):
        super().__init__(hdr_cls = HCIEvtHdr, **kwargs)

    def payload_len(self):
        return self.hdr.plen

@evt
@dataclass(eq=False)
class CommandComplete:
    code = 0x0E
    sig = '<BH'

    num_cmds: int
    cmd_opcode: int

@evt
@dataclass(eq=False)
class CommandStatus:
    code = 0x0F
    sig = '<BBH'

    status: int
    num_cmds: int
    cmd_opcode: int

