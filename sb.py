#!/usr/bin/env python3

import abc
import collections
import contextvars
import logging
import threading
import asyncio
import struct
import time
import sys
import dataclasses
import typing

cv = contextvars.ContextVar('var', default='def')

@dataclasses.dataclass
class DCUncle:
    ocf = 0x2222
    type : str
    dd : int
 
    def __init__(self, type: str = None):
        print(f'Uncle init')

@dataclasses.dataclass
class DCParent:
    ocf = 0x1234
    name: str = 'defstr'
    data: bytearray = None

    def __init__(self, name: str):
        print(f'Parent init')

    def __post_init__(self):
        print(f'Parent post-init')

    def talk(self):
        print(f'Parent: {self.name}')

@dataclasses.dataclass
class DCChild(DCParent):
    pbf = 0x3
    age: int = 0

    def __init__(self, name: str, age: int):
        self.unc = DCUncle()
        print(f'Child init')

    def __post_init__(self):
        print(f'Child post-init')

    def talk(self):
        print(f'Child: {self.name}:{self.age}')


async def say_after(delay, what):
    cv.set('say_after')
    print(f'say_after: {delay} thread:{threading.current_thread().native_id}'
          f' loop:{id(asyncio.get_running_loop())}'
          f' task {asyncio.current_task().get_name()}')
    await asyncio.sleep(delay)
    print(f'cv3: {cv.get()}')
    print(what)
    print(f'say_after complete: thread:{threading.current_thread().native_id}'
          f' loop:{id(asyncio.get_running_loop())}')

async def mycoro():
    print(f'cv5: {cv.get()}')
    await asyncio.sleep(1)

async def mycoro2():
    print('entering mycoro2')
    await asyncio.sleep(1)
    print('exiting mycoro2')

async def aio_sb():
    print(f'aio_sb: task {asyncio.current_task().get_name()}')

    done, pend = await asyncio.wait([say_after(1, "abc"), say_after(2, "ced")])
    return

    print(f'cv1: {cv.get()}')
    cv.set('aio_sb')
    print(f"before task1 {time.strftime('%X')} on {threading.current_thread().native_id}")
    task1 = asyncio.create_task(say_after(1, 'hello')) 
    print(f"before task2 {time.strftime('%X')} on {threading.current_thread().native_id}")
    task2 = asyncio.create_task(say_after(3, 'world'))
    print(f'cv2: {cv.get()}')

    print(f"started at {time.strftime('%X')} on {threading.current_thread()}")
    await task1
    await task2
    print(f"finished at {time.strftime('%X')} on {threading.current_thread()}")
    print(f'cv4: {cv.get()}')

    #await mycoro()
    #print(f'cv6: {cv.get()}')

    #print(f'calling mycoro2')
    #await mycoro2()
    #print(f'called mycoro2')


def log_layer():
    logger = logging.getLogger('sb.layer')
    logger.info('test log_layer')

def log_sb():
    logger = logging.getLogger('sb')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s -'
            ' %(message)s', datefmt='%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info('test log_sb')
    log_layer()

    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s -'
    #        ' %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    #logging.debug(f"debug test: {sys.argv[0]}")

def dc_sb():
    p = DCParent('abc')
    c = DCChild('def', 3)
    c2 = DCChild(age=7, name='c2')
    u = DCUncle()

    p.talk()
    c.talk()
    c2.talk()

    print(type(DCParent))
    print([i.name for i in dataclasses.fields(c)])
    print(dataclasses.asdict(c))
    print(dataclasses.astuple(c))

class NTTest(typing.NamedTuple):
    ocf = 0x3333
    name: str
    age: int


class NTClass(typing.NamedTuple):
    ocf = 0x000C
    sig = '<HH'
    le_scan_enable: int = 0
    filter_dups: int = 0

    # This will fail
    #def __init__(self):
    #    pass

    def unpack(self):
        print('NTClass unpack')
    
    #def __repr__(self):
    #    return "NTClass_repr"

    def __str__(self):
        return "NTClass_str"

def nt_sub(cls: typing.Type[typing.NamedTuple]):
    #print(cls.ocf)
    #print(inst)
    #print(inst._fields)

    b = bytes([1, 2, 3, 4])
    t = struct.unpack(cls.sig, b)
    print(t)
    inst = cls(*t)
    print(inst)
    if inst.unpack:
        inst.unpack()

def nt_sub2(tup: typing.NamedTuple):
    print(tuple(tup))
    b = struct.pack(tup.sig, *tuple(tup))
    bb = struct.pack(tup.sig, 12, 11)
    print(b)
    print(bb)

def nt_sb():
    #n = NTTest('abc', 12)
    # setting it fails
    # n.name = 'def'
    #print(n)
    #nt_sub(NTClass)

    i = NTClass(12, 11)
    print(i)
    print(i._fields)
    nt_sub2(i)
    print(f'here is i: {i} and its repr: {repr(i)}')
    

    #i = NTClass(le_scan_enable=3, filter_dups=4)
    #print(i)
    #print(f'{i.ocf}, {i.sig}')
    #print(i._fields)

class ABCParent(abc.ABC):

    def __init__(self):
        print('ABCParent init')

    @classmethod
    @abc.abstractmethod
    def cm(cls):
        '''cm'''

class ABCChild(ABCParent):

    def __init__(self):
        print('ABCChild init')

    @classmethod
    def cm(cls):
        print(f'cm: {cls}')


def abc_sb():

    abc = ABCParent()
    abc = ABCChild()
    ABCChild.cm()

def main():
    #nt_sb()
    #dc_sb()
    #log_sb()
    abc_sb()
    #asyncio.run(aio_sb())

if __name__ == '__main__':
    main()
