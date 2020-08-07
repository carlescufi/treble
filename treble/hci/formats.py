from typing import NamedTuple

class Cmds:

    class Reset(NamedTuple):
        ogf = 0x03
        ocf = 0x003

    class LESetScanEnable(NamedTuple):
        ocf = 0x000C
        sig = '<BB'
        le_scan_enable: int
        filter_dups: int

class Evts:

    class CommandComplete(NamedTuple):
        code = 0x0E
        sig = '<BH'

        num_cmds: int
        cmd_opcode: int

    class CommandStatus(NamedTuple):
        code = 0x0F
        sig = '<BBH'

        status: int
        num_cmds: int
        cmd_opcode: int

class LEMetaEvts:
    pass
