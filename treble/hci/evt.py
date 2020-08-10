from typing import NamedTuple

all = dict()
def evt(cls):
    evts[cls.code] = cls
    return cls

@evt
class CommandComplete(NamedTuple):
    code = 0x0E
    sig = '<BH'

    num_cmds: int
    cmd_opcode: int

@evt
class CommandStatus(NamedTuple):
    code = 0x0F
    sig = '<BBH'

    status: int
    num_cmds: int
    cmd_opcode: int

