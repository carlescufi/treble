#!/usr/bin/env python3

import logging
import threading
import asyncio
import time
import sys


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

def main():
    log_sb()
    #asyncio.run(aio_sb())

if __name__ == '__main__':
    main()
