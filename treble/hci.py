
from asyncio import create_task, Queue
from .packet import *
import logging

from .transport.hci_transport import HCITransport, HCI_TRANSPORT_UART
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
        create_task(self._rx_task())
        # Start TX task
        self._tx_q = Queue()
        create_task(self._tx_task())

    async def _rx_task(self):
        log.debug('rx task started')
        while True:
            pkt = await self._transport.recv()
            log.debug(f'pkt rx: {pkt}')
        
    async def _tx_task(self):
        log.debug('tx task started')
        while True:
            pkt = await self._tx_q.get()
            log.debug('pkt tx: {pkt}')
            await self._transport.send(pkt)

    def send_cmd(self, pkt: HCICmd):
        pkt = HCICmd(Reset)
        self._tx_q.put_nowait(pkt)
