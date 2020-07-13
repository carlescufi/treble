#!/usr/bin/env python3

import logging
import threading
import asyncio
import struct
import time
import sys
import dataclasses
import typing

@dataclasses.dataclass
class DCParent:
    ocf = 0x1234
    name: str = 'defstr'

    def talk(self):
        print(f'Parent: {self.name}')

@dataclasses.dataclass
class DCChild(DCParent):
    pbf = 0x3
    age: int = 0

    def talk(self):
        print(f'Child: {self.name}:{self.age}')


class NTTest(typing.NamedTuple):
    name: str
    age: int


async def say_after(delay, what):
    print(f'say_after: {delay} thread:{threading.current_thread()}'
          f' loop:{id(asyncio.get_running_loop())}')
    await asyncio.sleep(delay)
    print(what)

async def aio_sb():
    task1 = asyncio.create_task(say_after(1, 'hello')) 
    task2 = asyncio.create_task(say_after(3, 'world'))

    print(f"started at {time.strftime('%X')} on {threading.current_thread()}")
    await task1
    await task2
    print(f"finished at {time.strftime('%X')} on {threading.current_thread()}")

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

    p.talk()
    c.talk()
    c2.talk()

    print(dataclasses.fields(c))
    print(dataclasses.asdict(c))
    print(dataclasses.astuple(c))

def nt_sb():
    n = NTTest('abc', 12)
    # setting it fails
    # n.name = 'def'
    print(n)


class NTClass(typing.NamedTuple):
    ocf = 0x000C
    sig = '<BB'
    le_scan_enable: int = 0
    filter_dups: int = 0

def nt_struct():
    i = NTClass(le_scan_enable=3, filter_dups=4)
    print(i)
    print(f'{i.ocf}, {i.sig}')

def main():
    nt_struct()
    #nt_sb()
    #dc_sb()
    #log_sb()
    #asyncio.run(aio_sb())

if __name__ == '__main__':
    main()
