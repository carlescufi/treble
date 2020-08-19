import asyncio
from abc import ABC, abstractmethod
from typing import Optional

HCI_TRANSPORT_UART = 'uart'

class HCITransport(ABC):
    '''Abstract superclass for an HCI transport.'''

    def __init__(self, name: str):
        '''HCI transport initialization.'''
        self.name = name

    @abstractmethod
    def open(self, dev: str, **kwargs) -> None:
    	'''Open transport.'''

    @abstractmethod
    async def close(self):
    	'''Close transport.'''

    @abstractmethod
    async def send(self, data: bytearray) -> None:
    	'''Send data, blocking.'''

    @abstractmethod
    async def recv(self, timeout: int) -> Optional[bytearray]:
    	'''Receive data, blocking.'''

    def repr():
        return f'{self.__class__}, {self.name}'
