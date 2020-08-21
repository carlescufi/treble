# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import logging
import textwrap

from . import hci
from .hci.cmd import HCICmd
from .hci.evt import HCIEvt
from .packet import HCIACLData
from .util import timestamp

log = logging.getLogger('treble.mon')

LINEW = 120
TX = '<'
RX = '>'
DIR_LEN = len('{dir} '.format(dir=TX))
CMD_FMT = 'HCI Command: {cmd} (0x{ocf:02x}|0x{ogf:04x})'
CMD_FMT_LEN = len(CMD_FMT.format(cmd='', ocf=1, ogf=1))
EVT_FMT = 'HCI Event: {evt} (0x{code:02x})'
EVT_FMT_LEN = len(EVT_FMT.format(evt='', code=1))
POSTFIX_FMT = '#{count} [tre{cidx}] {timestamp()}'

class Monitor:

    def __init__(self):
        self.counts = {}

    def feed_rx(self, cidx, pkt):
        self._feed(RX, cidx, pkt)

    def feed_tx(self, cidx, pkt):
        self._feed(TX, cidx, pkt)

    def _feed(self, dir: str, cidx: int, pkt):
        print(pkt)
        print(type(pkt))
        if isinstance(pkt, bytes) or isinstance(pkt, bytearray):
            raise NotImplementedError
        elif dir == TX and isinstance(pkt, HCICmd):
            self._cmd(pkt.data)
        elif dir == RX and isinstance(pkt, HCIEvt):
            self._evt(pkt.data)
        elif isinstance(pkt, HCIACLData):
            self._acl(dir, pkt.data)
        else:
            raise NotImplementedError

    def _cmd(self, data: bytes):
        #cmd = HCICmd(data)
        #cmd.unpack_header()
        pass

    def _evt(self, pkt: bytes):
        pass

    def _acl(self, dir: str, pkt: bytes):
        pass

    def _get_name(self, cls):
        return inspect.getdoc(cls)
