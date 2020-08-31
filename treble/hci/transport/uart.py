# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import errno
import logging
import serial
import threading
from typing import Optional

from .transport import HCITransport, HCI_TRANSPORT_UART
from ...packet import Packet, HCIACLData
from ..cmd import HCICmd
from ..evt import HCIEvt

log = logging.getLogger('treble.hci.transport.uart')

class StreamTransport(HCITransport):

    # Packet indicators
    IND_NONE = 0x0
    IND_CMD = 0x1
    IND_ACL = 0x2
    IND_SCO = 0x3
    IND_EVT = 0x4

    def __init__(self, name: str):
        super().__init__(name)
        # Init RX states
        self._rx_state = UART.IND_NONE
        self._rx_pkt = None
        self._rx_remain = 0
        self._rx_hdr = False

    def _rx(self, data: bytes) -> Optional[Packet]:
        log.debug(f'read: {data.hex("-")}')
        idx : int = 0
        dlen : int = len(data)
        while(dlen):

            # copy as much as available
            if self._rx_remain:
                clen = min(self._rx_remain, dlen)
                # Use += to ensure in-place concatenation without creating a
                # new object  This should be faster than extend()
                self._rx_pkt.data += data[idx:idx + clen]
                idx += clen
                self._rx_remain -= clen
                dlen -= clen
                if self._rx_remain:
                    # More bytes required
                    return None

            if self._rx_state == UART.IND_NONE:
                ind = data[0]
                idx += 1
                dlen -= 1
                self._rx_state = ind
                if ind == UART.IND_ACL:
                    self._rx_pkt = HCIACLData()
                    self._rx_remain = self._rx_pkt.header_len()
                elif ind == UART.IND_EVT:
                    self._rx_pkt = HCIEvt()
                    self._rx_remain = self._rx_pkt.header_len()
                else:
                    raise RuntimeError(f'Unexpected or invalid indicator {ind}')
            elif not self._rx_hdr:
                # Header complete, parse it
                self._rx_pkt.unpack_header()
                if self._rx_state == UART.IND_ACL:
                    self._rx_remain = self._rx_pkt.payload_len()
                else:
                    self._rx_remain = self._rx_pkt.payload_len()
                self._rx_hdr = True
            else:
                pkt = self._rx_pkt
                self._rx_pkt = None
                self._rx_state = UART.IND_NONE
                self._rx_hdr = False
                return pkt

class UARToTCP(StreamTransport):
    pass

class UART(StreamTransport):

    # Initial baudrate
    INIT_BAUDRATE = 9600

    def __init__(self):
        super().__init__(HCI_TRANSPORT_UART)
        self._open = False
        self._closing = False
        self._rx_q = asyncio.Queue()
        self._loop = asyncio.get_event_loop()
        self._tx_lock = asyncio.Lock(loop=self._loop)

    def open(self, dev : str, **kwargs) -> None:
        if self._open or self._closing:
            raise OSError(errno.EEXIST)

        self._baudrate = kwargs.get('baudrate')
        if not self._baudrate:
            raise RuntimeError('missing baudrate')
        if self._baudrate == UART.INIT_BAUDRATE:
            raise RuntimeError('invalid baudrate')

        # Spec-mandated values
        kwargs['bytesize'] = 8
        kwargs['parity'] = 'N'
        kwargs['stopbits'] = 1
        kwargs['rtscts'] = True
        # Wait forever in the rx thread
        kwargs['timeout'] = None
        kwargs['write_timeout'] = None
        # Force baudrate to a slow, unusable one initially
        kwargs['baudrate'] = UART.INIT_BAUDRATE
        log.info(f'opening serial port device {dev} at {self._baudrate:,} baud')
        try:
            self._serial = serial.Serial(dev, **kwargs)
        except serial.SerialException as e:
            raise OSError(*e.args) from None
        # Force a baudrate change, some onboard debuggers require seeing a
        # baudrate change in order to start hardware flow control
        self._serial.baudrate = self._baudrate
        self._open = True
        self._rx_thread = threading.Thread(target=self._rx_thread_fn,
                                           daemon=True)
        self._rx_thread.start()

    async def close(self):
        async with self._tx_lock():
            self._closing = True
            self._open = False
            await self._loop.run_in_executor(None, self._rx_thread.join())
            await self._rx_q.join()
            self._serial.cancel_read()
            self._serial.close()
            self._closing = False

    async def send(self, pkt: Packet) -> None:
        if not self._open:
            raise OSError(errno.ENODEV)
        async with self._tx_lock:
            ind : int = UART.IND_NONE
            if isinstance(pkt, HCIACLData):
                ind = UART.IND_ACL
            elif isinstance(pkt, HCICmd):
                ind = UART.IND_CMD
            else:
                raise RuntimeException('invalid packet type')

            txd = bytes([ind]) + pkt.data
            log.debug(f'writing {txd.hex("-")}')
            try:
                written = await self._loop.run_in_executor(None,
                                                           self._serial.write,
                                                           txd)
                #assert(written == 1)
            except serial.SerialException as e:
                log.error(f'rx exception: {e}')
                raise OSError(e.errno, e.strerror) from None

    async def recv(self, timeout: int = 0) -> Optional[Packet]:
        if not self._open:
            raise OSError(errno.ENODEV)
        pkt = await self._rx_q.get()
        self._rx_q.task_done()
        return pkt

    def _rx_enq(self, pkt: Packet) -> None:
        log.debug(f'enq pkt: {pkt}')
        self._rx_q.put_nowait(pkt)

    def _rx_thread_fn(self) -> None:
        id = threading.current_thread()
        log.debug(f'rx thread started: {id}')
        # Drain UART
        self._serial.reset_input_buffer()
        while self._open and self._serial.is_open:
            try:
                data = self._serial.read(max(1, self._serial.in_waiting))
                pkt = self._rx(data)
                if pkt:
                    # Packet completed, dispatch it
                    self._loop.call_soon_threadsafe(self._rx_enq, pkt)
            except Exception as e:
                log.error(f'rx exception: {e}')
                break

        self._open = False
        # The public RX path is now disabled
        self._rx_enq(None)
        log.debug(f'rx thread exited: {id}')

