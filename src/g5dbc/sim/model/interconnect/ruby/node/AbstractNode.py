from abc import ABCMeta, abstractmethod

from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby import Sequencer, m5_RubySystem
from g5dbc.sim.m5_objects.sim import m5_SubSystem
from g5dbc.sim.model.topology import NodeSpec

from ..controller.AbstractController import AbstractController


class AbstractNode(m5_SubSystem):
    """
    Abstract Ruby Controller Node
    """

    __metaclass__ = ABCMeta

    def __init__(self, node_id: NodeSpec):
        super().__init__()
        self._ctrl_id = node_id.ctrl_id
        self._router_id = node_id.router_id
        self._numa_id = node_id.numa_id
        self._exclusive_router = node_id.needs_exclusive_router

    def get_ctrl_id(self) -> int:
        """
        Get controller id
        """
        return self._ctrl_id

    def get_router_id(self) -> int:
        """
        Get assigned router id
        """
        return self._router_id

    def get_numa_id(self) -> int:
        """
        Get NUMA id
        """
        return self._numa_id

    def set_router_id(self, router_id: int) -> int:
        """
        Update assigned router id
        """
        self._router_id = router_id
        return self._router_id

    def needs_exclusive_router(self) -> bool:
        """
        Needs exclusive router
        """
        return self._exclusive_router

    def set_clock_domain(self, clk_domain) -> None:
        for seq in self.get_sequencers():
            seq.set_clock_domain(clk_domain)

        for ctr in self.get_controllers():
            ctr.set_clock_domain(clk_domain)

    @abstractmethod
    def create_controller(self, config: Config, ruby_system: m5_RubySystem):
        """
        Create Node Controllers
        """

    @abstractmethod
    def get_controllers(self) -> list[AbstractController]:
        """
        Get Node Controllers
        """

    @abstractmethod
    def get_sequencers(self) -> list[Sequencer]:
        """
        Get Node Controller Sequencers
        """

    @abstractmethod
    def set_downstream(self, ctrls: list[AbstractController]) -> None:
        """
        Sets ctrls as downstream from this node
        """

    @classmethod
    def node_type(cls) -> str:
        return cls._node_class
