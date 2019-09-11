
import logging
import os
import sys

from .hci import HCI
from .version import __version__

from treble import hci

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style

style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})

def main(argv=None):
    session = PromptSession(style=style)

    print('Treble {} (pid {})-- BLE Host. Type \'q\' to '
          'quit.\n'.format(__version__, os.getpid()))
    
    logging.basicConfig(level=logging.DEBUG)
    hci = HCI('h4', '/dev/ttyACM0',  baudrate=1000000)
    return 0

    while True:
        try:
            text = session.prompt('>> ')
        except KeyboardInterrupt:
            continue  # Control-C pressed. Try again.
        except EOFError:
            break  # Control-D pressed.
        
        if text == 'q' or text == 'quit':
            break

    print('GoodBye!')
    return 0


if __name__ == "__main__":
    main()
