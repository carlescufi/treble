
from asyncio import create_task, Queue
from ..packet import *
import logging

from .transport.transport import HCITransport, HCI_TRANSPORT_UART
from .transport.uart import UART

log = logging.getLogger('treble.hci')

class HCI:

    def __init__(self, name, dev, **kwargs):
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

    async def _rx_task(self):
        log.debug('rx task started')
        while True:
            pkt = await self._transport.recv()
            if isinstance(pkt, HCIEvt):
                self._rx_evt(pkt)
            elif instance(pkt, HCIACLData):
                self._rx_acl(pkt)
            else:
                raise RuntimeError
            
 
    def _rx_evt(self, evt: HCIEvt):
        log.debug(f'evt rx: {evt}')

    def _rx_acl(self, acl: HCIACLData):
        log.debug(f'acl rx: {evt}')

    async def _tx_cmd_task(self):
        log.debug('tx cmd task started')
        while True:
            #await self._tx_cmd_sem
            pkt = await self._tx_cmd_q.get()
            log.debug('pkt tx: {pkt}')
            await self._transport.send(pkt)

    def send_cmd(self, pkt: HCICmd):
        self._tx_cmd_q.put_nowait(pkt)
