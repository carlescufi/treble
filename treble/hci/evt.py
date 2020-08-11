from dataclasses import dataclass
import typing

all = dict()
def evt(cls):
    evts[cls.code] = cls
    return cls

@evt
@dataclass(eq=False)
class CommandComplete(NamedTuple):
    code = 0x0E
    sig = '<BH'

    num_cmds: int
    cmd_opcode: int

@evt
@dataclass(eq=False)
class CommandStatus(NamedTuple):
    code = 0x0F
    sig = '<BBH'

    status: int
    num_cmds: int
    cmd_opcode: int

