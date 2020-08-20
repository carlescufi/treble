# Copyright (c) 2020 Carles Cufí
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
import sys

#from treble.controller import Controller
from treble.version import __version__
from treble import hci

#from treble.hci.cmd import Reset
#from treble.packet import HCICmd

from treble.controller import Controller
from treble.packet import HCICmd

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style

style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})

log = logging.getLogger('treble')

def die(msg: str):
    print(msg)
    sys.exit(1)

def init_logging():
    # Set the treble root level: process everything
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(style='{', fmt='{asctime}.{msecs:03.0f}:'
            '{module:4.4}:'
            '{levelname:3.3}: {message}', datefmt='%H:%M:%S')
    # Stream handler for DEBUG and INFO records
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(formatter)
    ch.addFilter(lambda record: record.levelno <= logging.INFO)
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)
    # Stream handler for WARNING, ERROR and CRITICAL records
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(formatter)
    ch.setLevel(logging.WARNING)
    log.addHandler(ch)

    # Set logging levels
    logging.getLogger("treble.controller").setLevel(logging.INFO)
    logging.getLogger("treble.hci").setLevel(logging.INFO)
    logging.getLogger("treble.hci.transport").setLevel(logging.INFO)
    logging.getLogger("treble.hci.transport.uart").setLevel(logging.INFO)
 

async def init():

    print(f'treble {__version__} (pid {os.getpid()}) -- BLE Host. Type \'q\' '
          f'to quit.\n')
    init_logging()
    log.debug('init')
    try:
        ctlr = Controller('uart', '/dev/ttyACM0',  baudrate=1000000)
    except OSError as e:
        die(e)

    await ctlr.open()
    #pkt = HCICmd(hci.cmd.Reset)
    #pkt = treble.packet.HCICmd()
    #for i in range(5):
    #    log.debug('tx_cmd')
    #    #ctlr._hci.tx_cmd(pkt)
    #    await ctlr._hci.send_cmd(pkt)
    #return 0



async def interactive_shell():
    return
    # Create Prompt.
    session = PromptSession(">> ")

    # Run echo loop. Read text from stdin, and reply it back.
    while True:
        try:
            text = await session.prompt_async()
            print('You said: "{0}"'.format(text))

            if text == 'q' or text == 'quit':
                break

        except (EOFError, KeyboardInterrupt):
            return

async def _main():
    await init()
    with patch_stdout():
        try:
            await interactive_shell()
        finally:
            print("caught")
        print("Quitting event loop. Bye.")


def main():
    asyncio.run(_main())
