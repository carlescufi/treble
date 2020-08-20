# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import logging
from . import hci
from . import mon

log = logging.getLogger('treble.controller')

class Controller:

    def __init__(self, name, dev, **kwargs):
        self._mon = mon.Monitor()
        self._hci = hci.host.HCIHost(name, dev, self._mon, **kwargs)

    async def open(self):
        await self._hci.open()

    async def close(self):
        await self._hci.close()
