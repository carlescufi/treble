# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
import time

log = logging.getLogger('treble.util')

pyver = sys.version_info
assert pyver.major == 3

def timestamp() -> str:
    t = time.time()
    s = time.strftime("%H:%M:%S", time.localtime(t))
    s += f'.{(t % 1) * 1000000:06.0f}'
    return s

def hex(b: bytes, sep: str) -> str:
    if pyver.minor >= 8:
        return b.hex(sep)
    else:
        s = b.hex()
        return sep.join([''.join(c) for c in zip(*[iter(s)]*2)])

