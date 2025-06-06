from abc import ABC, ABCMeta, abstractmethod


class NetworkRouter:
    """
    NetworkRouter
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_router_id(self) -> int:
        """ """
