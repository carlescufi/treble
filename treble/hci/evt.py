import typing

class CommandComplete(typing.NamedTuple):
    code = 0x0E
    sig = '<BH'

    num_cmds: int
    cmd_opcode: int
    

class CommandStatus(typing.NamedTuple):
    code = 0x0F
    sig = '<BBH'

    status: int
    num_cmds: int
    cmd_opcode: int

