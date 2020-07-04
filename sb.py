#!/usr/bin/env python3

import threading
import asyncio
import time

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

def main():
    asyncio.run(aio_sb())

if __name__ == '__main__':
    main()
