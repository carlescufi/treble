
import asyncio
import logging
import os
import sys

from .controller import Controller
from .version import __version__

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

async def interactive_shell():
    # Create Prompt.
    session = PromptSession(">> ")

    print('Treble {} (pid {})-- BLE Host. Type \'q\' to '
          'quit.\n'.format(__version__, os.getpid()))
    logging.basicConfig(level=logging.DEBUG)
    ctlr = Controller('uart', '/dev/ttyACM0',  baudrate=1000000)
    ctlr._hci.send_cmd(None)
    #return 0


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
    with patch_stdout():
        try:
            await interactive_shell()
        finally:
            print("caught")
        print("Quitting event loop. Bye.")


def main():
    asyncio.run(_main())
