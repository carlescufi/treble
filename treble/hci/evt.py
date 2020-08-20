# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
import typing

all = dict()
def evt(cls):
    all[cls.code] = cls
    return cls

@evt
@dataclass(eq=False)
class CommandComplete:
    code = 0x0E
    sig = '<BH'

    num_cmds: int
    cmd_opcode: int

@evt
@dataclass(eq=False)
class CommandStatus:
    code = 0x0F
    sig = '<BBH'

    status: int
    num_cmds: int
    cmd_opcode: int

