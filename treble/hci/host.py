# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

from asyncio import create_task, Queue, Event, BoundedSemaphore, wait_for, \
                    TimeoutError, CancelledError
import inspect
import logging

from . import cmd
from .cmd import HCICmd
from . import evt
from .evt import HCIEvt
from ..packet import *
from ..mon import Monitor
from .transport.transport import HCITransport, HCI_TRANSPORT_UART, \
                                 HCI_TRANSPORT_TCP
from .transport.uart import UART, UARToTCP

log = logging.getLogger('treble.hci')

ATTR_EVT_HANDLER = '_evt_handler'
def handlers(cls):
    cls.evt_handlers = dict()
    for t in inspect.getmembers(cls, predicate=inspect.isfunction):
        f = t[1]
        if hasattr(f, ATTR_EVT_HANDLER):
            cls.evt_handlers[getattr(f, ATTR_EVT_HANDLER)] = f
    return cls

def evt_handler(evt_cls):
    def wrapper(fun):
        setattr(fun, ATTR_EVT_HANDLER, evt_cls.code)
        return fun
    return wrapper

@handlers
class HCIHost:

    def __init__(self, name: str, dev: str, mon: Monitor=None, **kwargs):
        self._dev = dev
        self._kwargs = kwargs
        self._mon = mon
        if (name == HCI_TRANSPORT_UART):
            self._transport = UART()
        elif (name == HCI_TRANSPORT_TCP):
            self._transport = UARToTCP()
        else:
            raise RuntimeError('Unknown transport type {}'.name)
        self._tx_cmd_q = Queue()
        # Bound to max 1, so we send only one command at a time
        self._tx_cmd_sem = BoundedSemaphore(value=1)

    async def open(self):
        try:
            await self._transport.open(self._dev, **self._kwargs)
        except OSError as e:
            #log.error(f'Unable to open serial port {e}')
            raise e from None

        # Start RX task
        self._rx_task = create_task(self._rx_task())
        # Start TX command task
        self._curr_cmd = None
        self._tx_cmd_task = create_task(self._tx_cmd_task())

        await self.init()

    async def close(self):
        await self._rx_task
        await self._tx_cmd_task
        self._transport.close()

    async def init(self):
        # Reset the controller first
        log.debug('init: Reset')
        pkt = HCICmd(cmd.Reset)
        await self.send_cmd(pkt)
        log.debug('init: ReadLocalVersionInformation')
        pkt = HCICmd(cmd.ReadLocalVersionInformation)
        await self.send_cmd(pkt)

    async def _rx_task(self):
        log.debug('rx task started')
        while True:
            try:
                pkt = await self._transport.recv()
            except CancelledError:
                # Here for compatibility with 3.7
                raise
            except Exception as e:
                log.debug(f'_rx_task: {e}')
            else:
                if not pkt:
                    # Broken RX Path
                    log.debug('_rx_task exiting')
                    break
                elif self._mon:
                    self._mon.feed_rx(0, pkt)

            if isinstance(pkt, HCIEvt):
                self._rx_evt(pkt)
            elif instance(pkt, HCIACLData):
                self._rx_acl(pkt)
            else:
                log.error('Invalid rx type: {type(pkt)}')

    def _rx_evt(self, evt: HCIEvt):
        log.debug(f'evt rx: {evt}')
        # Look for a handler
        try:
            handler = self.evt_handlers[evt.hdr.code]
        except KeyError:
            log.warn(f'Discarding event with code: {evt.hdr.code}')
        else:
            handler(self, evt)

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
            except CancelledError:
                # Here for compatibility with 3.7
                raise
            except TimeoutError:
                log.debug('_tx_cmd_task: sem timeout: exiting')
                return

            assert self._curr_cmd == None
            self._curr_cmd = pkt
            log.debug(f'_tx_cmd curr set')

            try:
                await self._transport.send(pkt)
            except OSError as e:
                log.debug('_tx_cmd_task: send error: exiting')
                return
            else:
                if self._mon:
                    self._mon.feed_tx(0, pkt)

    def tx_cmd(self, pkt: HCICmd) -> None:
        self._tx_cmd_q.put_nowait(pkt)

    async def send_cmd(self, pkt: HCICmd) -> HCIEvt:
        pkt.event.clear()
        self.tx_cmd(pkt)
        try:
            await wait_for(pkt.event.wait(), 15)
        except TimeoutError:
            raise

    def _complete_cmd(self):
        log.debug(f'complete: {self._curr_cmd}')
        assert self._curr_cmd
        # Wake up a potential task waiting on completion
        self._curr_cmd.event.set()
        self._curr_cmd = None

        # The command itself is complete, allow the tx cmd task to move on to
        # the next queued command
        self._tx_cmd_sem.release()

    @evt_handler(evt.CommandComplete)
    def _evt_cc(self, evt: HCIEvt) -> None:
        log.debug(f'handling CC: {evt}')

        self._complete_cmd()

