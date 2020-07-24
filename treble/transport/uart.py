
import asyncio
import logging
import serial
import threading
from typing import Optional

from .hci_transport import HCITransport, HCI_TRANSPORT_UART
from ..packet import Packet, HCIACLData, HCICmd, HCIEvt

log = logging.getLogger('treble.transport.uart')

class UART(HCITransport):

    # Initial baudrate
    INIT_BAUDRATE = 9600

    # Packet indicators
    IND_NONE = 0x0
    IND_CMD = 0x1
    IND_ACL = 0x2
    IND_SCO = 0x3
    IND_EVT = 0x4

    def __init__(self):
        super().__init__(HCI_TRANSPORT_UART)

    def open(self, dev : str, **kwargs) -> None:
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
        log.info(f'opening serial port device {dev} with params {kwargs}')
        try:
            self._serial = serial.Serial(dev, **kwargs)
        except serial.SerialException as e:
            log.error(f'Unable to open serial port {dev}')
            return
        # Force a baudrate change, some onboard debuggers require seeing a
        # baudrate change in order to start hardware flow control
        self._serial.baudrate = self._baudrate
        self._open = True
        # Init RX states
        self._rx_state = UART.IND_NONE
        self._rx_pkt = None
        self._rx_remain = 0
        self._rx_hdr = False
        self._rx_q = asyncio.Queue()

        self._loop = asyncio.get_event_loop()
        self._tx_lock = asyncio.Lock(loop=self._loop)

        self._rx_thread = threading.Thread(target=self._rx_thread_fn,
                                           daemon=True)
        self._rx_thread.start()

    def close(self):
        self._open = False
        self._serial.cancel_read()
        self._serial.close()
        self._rx_thread.join()

    async def send(self, pkt: Packet) -> None:
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
                raise e

    async def recv(self, timeout: int = 0) -> Optional[Packet]:
        return await self._rx_q.get()

    def _rx_enq(self, pkt: Packet) -> None:
        log.debug(f'pkt: {pkt}')
        self._rx_q.put_nowait(pkt)

    def _rx(self, data: bytes) -> None:
        log.debug(f'_rx: {data.hex("-")}')
        idx : int = 0
        dlen : int = len(data)
        # Use += to ensure in-place concatenation without creating a new object
        # This should be faster than extend()
        #self._rx_bytes += data
        while(dlen):

            # copy as much as available
            if self._rx_remain:
                clen = min(self._rx_remain, dlen)
                self._rx_pkt.data += data[idx:idx + clen]
                idx += clen
                self._rx_remain -= clen
                dlen -= clen
                if self._rx_remain:
                    # More bytes required
                    return

            if self._rx_state == UART.IND_NONE:
                ind = data[0]
                idx += 1
                dlen -= 1
                self._rx_state = ind
                if ind == UART.IND_ACL:
                    self._rx_pkt = HCIACLData()
                    self._rx_remain = 4
                elif ind == UART.IND_EVT:
                    self._rx_pkt = HCIEvt()
                    self._rx_remain = 2
                else:
                    self.close()
                    raise RuntimeError(f'Unexpected or invalid indicator {ind}')
            elif not self._rx_hdr:
                # Header complete, parse it
                self._rx_pkt.unpack_header()
                if self._rx_state == UART.IND_ACL:
                    self._rx_remain = self._rx_pkt.hdr.dlen
                else:
                    self._rx_remain = self._rx_pkt.hdr.plen
                self._rx_hdr = True
            else:
                # Packet completed, dispatch it
                self._loop.call_soon_threadsafe(self._rx_enq, self._rx_pkt)
                self._rx_pkt = None
                self._rx_state = UART.IND_NONE
                self._rx_hdr = False

    def _rx_thread_fn(self) -> None:
        id = threading.current_thread()
        log.debug(f'rx thread started: {id}')
        # Drain UART
        self._serial.reset_input_buffer()
        while self._open and self._serial.is_open:
            try:
                data = self._serial.read(max(1, self._serial.in_waiting))
                self._rx(data)
            except Exception as e:
                log.error(f'rx exception: {e}')
                break

        log.debug(f'rx thread exited: {id}')

