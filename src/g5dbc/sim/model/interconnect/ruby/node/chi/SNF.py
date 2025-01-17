from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby import Sequencer, m5_RubySystem
from g5dbc.sim.model.interconnect.ruby.controller import AbstractController
from g5dbc.sim.model.interconnect.ruby.controller.chi import MemController
from g5dbc.sim.model.topology import NodeSpec

from ..AbstractNode import AbstractNode


class CHI_SNF_Base(AbstractNode):
    """
    CHI Subordinate Node
    """

    def __init__(self, node_id: NodeSpec):
        super().__init__(node_id)

    def create_controller(self, config: Config, ruby_system: m5_RubySystem):
        """
        Create CHI Subordinate Node
        """
        self.ctrl = MemController(
            config=config.memory.controller, ruby_system=ruby_system
        )

    def get_controllers(self) -> list[AbstractController]:
        return [self.ctrl]

    def get_sequencers(self) -> list[Sequencer]:
        return []


class SNF(CHI_SNF_Base):
    """
    Memory controller
    """

    _node_class = "SNF_Mem"


class SNF_ROM(CHI_SNF_Base):
    """
    ROM memory
    """

    _node_class = "SNF_ROM"
