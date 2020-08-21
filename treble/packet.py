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



