# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import logging
import time

log = logging.getLogger('treble.util')

def timestamp() -> str:
    t = time.time()
    s = time.strftime("%H:%M:%S", time.localtime(t))
    s += f'.{(t % 1) * 1000000:06.0f}'
    return s
