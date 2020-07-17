
import logging
import serial

from .hci_transport import HCITransport, HCI_TRANSPORT_H4

log = logging.getLogger('treble.h4')

class H4(HCITransport):

    # Packet indicators
    IND_CMD = 0x1
    IND_ACL = 0x2
    IND_SCO = 0x3
    IND_EVT = 0x4

    def __init__(self):
        super().__init__(HCI_TRANSPORT_H4)

    def open(self, dev, **kwargs):
        if not kwargs.get('baudrate'):
            raise RuntimeError('missing baudrate')
        # Spec-mandated values
        kwargs['bytesize'] = 8
        kwargs['parity'] = 'N'
        kwargs['stopbits'] = 1
        kwargs['rtscts'] = True 
        # 100ms read timeout
        kwargs['timeout'] = 0.01
        kwargs['write_timeout'] = None
        log.info('opening serial port device {} with params {}'
                 .format(dev, kwargs))
        ser = serial.Serial(dev, **kwargs)

    def close(self):
        pass

    def send(self, packet):
        log.debug('h4 send')

    def recv(self):
        log.debug('h4 recv')
