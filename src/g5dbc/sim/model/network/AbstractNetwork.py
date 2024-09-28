from abc import ABCMeta, abstractmethod

from g5dbc.sim.model.topology import AbstractTopology
from g5dbc.sim.model.interconnect.ruby.node import AbstractNode

class AbstractNetwork:
    """
    Abstract Network
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self, topology: AbstractTopology) -> None:
        """
        Initialize Network
        """

    @abstractmethod
    def connect_nodes(self, nodes: list[AbstractNode]):
        """
        Distribute nodes on the network
        """

    @abstractmethod
    def connect_interfaces(self):
        """
        connect interfaces on the network
        """

    @abstractmethod
    def get_num_virtual_networks(self) -> int:
        """
        """
