from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby import m5_RubySystem, Sequencer
from g5dbc.sim.model.interconnect.ruby.controller import AbstractController
from g5dbc.sim.model.interconnect.ruby.controller.chi import CacheController
from g5dbc.sim.model.topology import NodeSpec
from ..AbstractNode import AbstractNode


class RNF(AbstractNode):
    """
    CHI Fully coherent Request Node.
    """

    _node_class = "RNF"

    def __init__(self, node_id:NodeSpec ):
        super().__init__(node_id)

        self._core_id = node_id.core_id

        # All sequencers and controllers
        self._ctrls : list[AbstractController] = []

        # Last level controllers
        self._ll_ctrls : list[AbstractController] = []
    
    def get_core_id(self) -> int:
        return self._core_id

    def create_controller(self, config: Config, ruby_system: m5_RubySystem):
        """
        Create RNF controller
        """

        max_outstanding_l1i_req = config.caches["L1I"].sequencer.max_outstanding_requests
        max_outstanding_l1d_req = config.caches["L1D"].sequencer.max_outstanding_requests

        self.dcache = CacheController(
                ruby_system = ruby_system,
                config=config.caches["L1D"],
                #data_channel_size = config.network.data_width
            )

        self.icache = CacheController(
                ruby_system = ruby_system,
                config=config.caches["L1I"],
                #data_channel_size = config.network.data_width
            )

        self.dcache.connect_sequencer(Sequencer(
                ruby_system = ruby_system,
                #disable_sanity_check=True,
                max_outstanding_requests=max_outstanding_l1d_req
            ), dcache=True)

        self.icache.connect_sequencer(Sequencer(
                ruby_system = ruby_system,
                #disable_sanity_check=True,
                max_outstanding_requests=max_outstanding_l1i_req
            ))

        self._ll_ctrls = [self.dcache, self.icache]
        for c in self._ll_ctrls:
            self._ctrls.append(c)
        
        if "L2" in config.caches:
            self.add_L2_cache(config,ruby_system)

    def add_L2_cache(self, config: Config, ruby_system: m5_RubySystem):

        self.l2cache = CacheController(
            config=config.caches["L2"],
            ruby_system = ruby_system
        )

        for c in self._ll_ctrls:
            c.set_downstream([self.l2cache])

        self._ll_ctrls = [self.l2cache]
        for c in self._ll_ctrls:
            self._ctrls.append(c)

    def get_sequencers(self) -> list[Sequencer]:
        seqs = [self.dcache.sequencer, self.icache.sequencer]
        
        return seqs
    
    def get_controllers(self) -> list[AbstractController]:
        return self._ctrls

    def set_downstream(self, ctrls: list[AbstractController]) -> None:
        for c in self._ll_ctrls:
            c.set_downstream(ctrls)
