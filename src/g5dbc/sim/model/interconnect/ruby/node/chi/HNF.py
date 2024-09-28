from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby import m5_RubySystem, Sequencer
from g5dbc.sim.model.interconnect.ruby.controller import AbstractController
from g5dbc.sim.model.interconnect.ruby.controller.chi import CacheController
from g5dbc.sim.model.topology import NodeSpec
from ..AbstractNode import AbstractNode


class HNF(AbstractNode):
    """
    CHI HNF cache/directory controller.
    """

    _node_class = "HNF"

    def __init__(self, node_id: NodeSpec):
        super().__init__(node_id)
    
    def create_controller(self, config: Config, ruby_system: m5_RubySystem):
        self.ctrl = CacheController(
            config=config.caches["SLC"],
            ruby_system=ruby_system
            #data_channel_size=config.network.data_width,
            #transitions_per_cycle=transitions_per_cycle
        )

    def get_controllers(self) -> list[AbstractController]:
        return [self.ctrl]
    
    def get_sequencers(self) -> list[Sequencer]:
        return []

    def set_downstream(self, ctrls: list[AbstractController]) -> None:
        for c in [self.ctrl]:
            c.set_downstream(ctrls)
