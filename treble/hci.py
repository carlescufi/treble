
import logging

from .hci_transport import HCITransport, HCI_TRANSPORT_H4
from .h4 import H4

log = logging.getLogger('treble.hci')

class HCI:

    def __init__(self, name, dev, **kwargs):
        if (name == HCI_TRANSPORT_H4):
            log.debug('opening H4 transport')
            self._transport = H4()
            self._transport.open(dev, **kwargs)
        else:
            raise RuntimeError('Unknown transport type {}'.name)

    def send():
        print('send hci')
