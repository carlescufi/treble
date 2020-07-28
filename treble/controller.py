import logging
from .hci import hci

log = logging.getLogger('treble.controller')

class Controller:

    def __init__(self, name, dev, **kwargs):
        self._hci = hci.HCI(name, dev, **kwargs)

