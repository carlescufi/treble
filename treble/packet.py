# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

from asyncio import Event
from dataclasses import dataclass, astuple
import struct
import typing
from typing import Type, NamedTuple

class Packet:

    def __init__(self, data : bytes = None, copy=False):
        if data:
            self.data = bytearray(data) if copy else data
        else:
            self.data = bytearray()
        self.idx = 0

    def unpack(self, cls : type) -> object:
        assert cls.sig
        s = struct.calcsize(cls.sig)
        t = struct.unpack(cls.sig, self.data[self.idx : self.idx + s])
        self.idx += s
        return cls(*t)

    def pack(self, tup : object) -> None:
        self.data[:0] = struct.pack(tup.sig, *astuple(tup))

    def header_len(self):
        raise NotImplementedError

    def unpack_header(self):
        raise NotImplementedError

    def payload_len(self):
        raise NotImplementedError

@dataclass
class HCICmdHdr:
    sig = '<HB'
    opcode : int
    plen : int

@dataclass
class HCIEvtHdr:
    sig = '<BB'
    code : int
    plen : int

@dataclass
class HCIACLHdr:
    sig = '<HH'
    handle : int
    dlen : int

class HCIACLData(Packet):

    def __init__(self, data : bytes = None):
        super().__init__(data)

    def header_len(self):
        return struct.calcsize(HCIACLHdr.sig)

    def unpack_header(self):
            self.hdr = self.unpack(HCIACLHdr)

    def payload_len(self):
        return self.hdr.dlen

class HCIEvt(Packet):

    def __init__(self, data : bytes = None):
        super().__init__(data)

    def header_len(self):
        return struct.calcsize(HCIEvtHdr.sig)

    def unpack_header(self):
        self.hdr = self.unpack(HCIEvtHdr)

    def payload_len(self):
        return self.hdr.plen

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

