from dataclasses import dataclass
import enum
import typing

cmds = dict()
def cmd(ogf):
    def wrap(cls):
        cls.ogf = ogf.value
        opcode = (cls.ogf << 10) | cls.ocf
        cls.opcode = opcode
        cmds[opcode] = cls
        return cls
    return wrap

class OGF(enum.Enum):
    LINK_CONTROL = 1
    LINK_POLICY = 2
    CTLR_BB = 3
    INFO_PARAMS = 4
    STATUS_PARAMS = 5
    TESTING_CMDS = 6
    LE_CTLR_CMDS = 8

@cmd(OGF.CTLR_BB)
class Reset:
    ocf = 0x003

@cmd(OGF.INFO_PARAMS)
class ReadLocalVersionInformation:
    ocf = 0x001
    @dataclass
    class ReturnParams:
        sig = '<BHBHH'
        hci_ver: int
        hci_rev: int
        lmp_pal_ver: int
        manu_name: int
        lmp_pal_subver: int

@cmd(OGF.LE_CTLR_CMDS)
@dataclass(eq=False)
class LESetScanEnable:
    ocf = 0x00C
    sig = '<BB'
    le_scan_enable: int
    filter_dups: int
