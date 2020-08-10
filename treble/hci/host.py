
from asyncio import create_task, Queue, Event, BoundedSemaphore, wait_for, \
                    TimeoutError
from ..packet import *
from ..mon import Monitor
import logging

from .transport.transport import HCITransport, HCI_TRANSPORT_UART
from .transport.uart import UART

log = logging.getLogger('treble.hci')

class HCIHost:

    def __init__(self, name: str, dev: str, mon: Monitor=None, **kwargs):
        self._mon = mon
        if (name == HCI_TRANSPORT_UART):
            self._transport = UART()
            self._transport.open(dev, **kwargs)
        else:
            raise RuntimeError('Unknown transport type {}'.name)
        
        # Start RX task
        self._rx_task = create_task(self._rx_task())
        # Start TX command task
        self._tx_cmd_q = Queue()
        self._tx_cmd_task = create_task(self._tx_cmd_task())
        # Bound to max 1, so we send only one command at a time
        self._tx_cmd_sem = BoundedSemaphore(value=1)
        self._curr_cmd = None

    async def _rx_task(self):
        log.debug('rx task started')
        while True:
            try:
                pkt = await self._transport.recv()
            except Exception as e:
                raise
            else:
                if self._mon:
                    self._mon.feed_rx(pkt)

            if isinstance(pkt, HCIEvt):
                self._rx_evt(pkt)
            elif instance(pkt, HCIACLData):
                self._rx_acl(pkt)
            else:
                log.error('Invalid rx type: {type(pkt)}')
            
 
    def _rx_evt(self, evt: HCIEvt):
        # Unpack the event and find a handler
        log.debug(f'evt rx: {evt}')

    def _rx_acl(self, acl: HCIACLData):
        log.debug(f'acl rx: {evt}')

    async def _tx_cmd_task(self):
        log.debug('tx cmd task started')
        while True:
            pkt = await self._tx_cmd_q.get()
            log.debug(f'pkt tx: {pkt}')

            # Wait for the current command to complete
            try:
                await wait_for(self._tx_cmd_sem.acquire(), 10)
            except TimeoutError:
                raise
            
            assert self._curr_cmd == None
            self._curr_cmd = pkt

            try:
                await self._transport.send(pkt)
            except Exception as e:
                raise
            else:
                if self._mon:
                    self._mon.feed_tx(pkt)

    def tx_cmd(self, pkt: HCICmd) -> None:
        self._tx_cmd_q.put_nowait(pkt)

    async def send_cmd(self, pkt: HCICmd) -> HCIEvt:
        pkt.event.clear()
        self.tx_cmd(pkt)
        try:
            await wait_for(pkt.event.wait(), 15)
        except TimeoutError:
            raise

