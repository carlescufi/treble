
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

log = logging.getLogger('treble.cli')

def die(msg: str):
    print(msg)
    sys.exit(1)

async def init():

    print(f'treble {__version__} (pid {os.getpid()}) -- BLE Host. Type \'q\' '
          f'to quit.\n')
    logging.basicConfig(level=logging.DEBUG)
    try:
        ctlr = Controller('uart', '/dev/ttyACM0',  baudrate=1000000)
    except OSError as e:
        die(e)

    pkt = HCICmd(hci.cmd.Reset)
    #pkt = treble.packet.HCICmd()
    for i in range(5):
        log.debug('tx_cmd')
        #ctlr._hci.tx_cmd(pkt)
        await ctlr._hci.send_cmd(pkt)
    #return 0



async def interactive_shell():
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
