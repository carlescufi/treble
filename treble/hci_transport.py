from abc import ABC, abstractmethod

HCI_TRANSPORT_H4 = 'h4'

class HCITransport(ABC):
    '''Abstract superclass for an HCI transport.'''

    def __init__(self, name):
        '''HCI transport initialization.'''
        self.name = name

    @abstractmethod
    def open(self, dev, **kwargs):
    	'''Open transport.'''

    @abstractmethod
    def close(self):
    	'''Close transport.'''

    @abstractmethod
    def send(self):
    	'''Send data, blocking.'''

    @abstractmethod
    def recv(self):
    	'''Receive data, blocking.'''

    def repr():
        return '{}: {}'.format(self.__class__, self.name)
