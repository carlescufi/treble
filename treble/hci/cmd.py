from dataclasses import dataclass
import enum
from typing import NamedTuple

cmds = dict()
def cmd(cls):
    opcode = (cls.ogf << 10) | cls.ocf
    cmds[opcode] = cls
    return cls

@cmd
class Reset:
    ogf = 0x03
    ocf = 0x003

@cmd
class ReadLocalVersionInformation:
    ogf = 0x04
    ocf = 0x001
    @dataclass
    class ReturnParams:
        sig = '<BHBHH'
        hci_ver: int
        hci_rev: int
        lmp_pal_ver: int
        manu_name: int
        lmp_pal_subver: int

@cmd
@dataclass
class LESetScanEnable:
    ogf = 0x08
    ocf = 0x00C
    sig = '<BB'
    le_scan_enable: int
    filter_dups: int

