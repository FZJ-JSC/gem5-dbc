from abc import ABCMeta, abstractmethod
from enum import Enum

class LinkType(Enum):
    INT = 1
    EXT = 2

class NetworkLink:
    """
    Network Link
    """

    __metaclass__ = ABCMeta

    def __init__(self) -> None:
        pass
