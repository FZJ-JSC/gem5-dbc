from g5dbc.config import Config
from g5dbc.config.caches import CacheConf
from g5dbc.config.caches.controller import CacheCtrlConf
from g5dbc.config.caches.latency import Latency
from g5dbc.sim.m5_objects.ruby import m5_RubySystem
from g5dbc.sim.model.interconnect.ruby.controller import AbstractController
from g5dbc.sim.model.interconnect.ruby.controller.chi import CacheController
from g5dbc.sim.model.topology import NodeSpec

from ...Sequencer import Sequencer
from ..AbstractNode import AbstractNode


class RNI(AbstractNode):
    """
    I/O Coherent Request Node
    """

    _node_class = "RNI_Base"

    def __init__(self, node_id: NodeSpec):
        super().__init__(node_id)

    def create_controller(self, config: Config, ruby_system: m5_RubySystem):

        dummy_conf = CacheConf(
            name="DMA",
            size="1024",
            assoc=1,
            latency=Latency(data=0, tag=1),
            controller=CacheCtrlConf(
                allow_SD=False,
                is_HN=False,
                enable_DMT=False,
                enable_DCT=False,
                alloc_on_seq_acc=False,
                alloc_on_seq_line_write=False,
                alloc_on_atomic=False,
                alloc_on_readshared=False,
                alloc_on_readunique=False,
                alloc_on_readonce=False,
                alloc_on_writeback=False,
                dealloc_on_unique=False,
                dealloc_on_shared=False,
                dealloc_backinv_unique=False,
                dealloc_backinv_shared=False,
                send_evictions=False,
                number_of_TBEs=16,
                number_of_repl_TBEs=1,
                number_of_snoop_TBEs=1,
                number_of_DVM_TBEs=1,
                number_of_DVM_snoop_TBEs=1,
                unify_repl_TBEs=False,
            ),
        )

        self.dma = CacheController(config=dummy_conf, ruby_system=ruby_system)

        self.dma.connect_sequencer(
            Sequencer(ruby_system=ruby_system, clk_domain=ruby_system.clk_domain)
        )

        # @TODO
        # self.dma.connect_network(ruby_system.get_network())

    def get_controllers(self) -> list[AbstractController]:
        return [self.dma]

    def get_sequencers(self) -> list[Sequencer]:
        return [self.dma.sequencer]

    def set_downstream(self, ctrls: list[AbstractController]) -> None:
        for c in [self.dma]:
            c.set_downstream(ctrls)
