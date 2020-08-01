import typing

class Reset(typing.NamedTuple):
    ogf = 0x03
    ocf = 0x003

class LESetScanEnable(typing.NamedTuple):
    ocf = 0x000C
    sig = '<BB'
    le_scan_enable: int
    filter_dups: int


