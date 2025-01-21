from g5dbc.config.caches import CacheConf
from g5dbc.config.prefetcher import PrefetcherConf
from g5dbc.sim.factory.prefetcher import PrefetcherFactory
from g5dbc.sim.m5_objects import m5_AddrRange, m5_NULL
from g5dbc.sim.m5_objects.ruby import Sequencer, m5_RubyCache, m5_RubySystem
from g5dbc.sim.m5_objects.ruby.chi import m5_Cache_Controller
from g5dbc.sim.m5_objects.ruby.message import (
    MandatoryMessageBuffer,
    OrderedTriggerMessageBuffer,
    TriggerMessageBuffer,
    m5_MessageBuffer,
)

from ..AbstractController import AbstractController


class CacheController(m5_Cache_Controller, AbstractController):
    """
    CHI Cache controller
    """

    def __init__(self, config: CacheConf, ruby_system: m5_RubySystem):
        super().__init__(**config.controller.to_dict())
        self.ruby_system = ruby_system
        self.mandatoryQueue = MandatoryMessageBuffer(
            allow_zero_latency=(config.controller.mandatory_queue_latency == 0)
        )
        self.prefetchQueue = MandatoryMessageBuffer()
        self.triggerQueue = TriggerMessageBuffer()
        self.retryTriggerQueue = OrderedTriggerMessageBuffer()
        self.replTriggerQueue = OrderedTriggerMessageBuffer()
        self.reqRdy = TriggerMessageBuffer()
        self.snpRdy = TriggerMessageBuffer()

        self.cache = m5_RubyCache(
            dataAccessLatency=config.latency.data,
            tagAccessLatency=config.latency.tag,
            size=config.size,
            assoc=config.assoc,
            start_index_bit=config.block_size_bits,
            resourceStalls=config.resource_stalls,
            is_icache=config.is_icache(),
        )

        # Default No prefetcher
        self.use_prefetcher = False
        self.prefetcher = m5_NULL
        # Default No sequencer
        self.sequencer = m5_NULL

    def set_prefetcher(self, config: PrefetcherConf | None):
        if config is not None:
            self.use_prefetcher = True
            self.prefetcher = PrefetcherFactory.create(config)

    def connect_network(self, network) -> None:
        """
        Connect CHI input/output ports to network
        """

        self.reqOut = m5_MessageBuffer()
        self.rspOut = m5_MessageBuffer()
        self.snpOut = m5_MessageBuffer()
        self.datOut = m5_MessageBuffer()
        self.reqIn = m5_MessageBuffer()
        self.rspIn = m5_MessageBuffer()
        self.snpIn = m5_MessageBuffer()
        self.datIn = m5_MessageBuffer()

        self.reqOut.out_port = network.in_port
        self.rspOut.out_port = network.in_port
        self.snpOut.out_port = network.in_port
        self.datOut.out_port = network.in_port
        self.reqIn.in_port = network.out_port
        self.rspIn.in_port = network.out_port
        self.snpIn.in_port = network.out_port
        self.datIn.in_port = network.out_port

    def connect_sequencer(self, sequencer: Sequencer, dcache: bool = False):
        self.sequencer = sequencer
        if dcache:
            self.sequencer.dcache = self.cache
        else:
            self.sequencer.dcache = m5_NULL

    def set_addr_ranges(self, addr_ranges: list[m5_AddrRange]) -> None:
        assert self.is_HN, "Setting address range for non-HN controller"
        self.addr_ranges = addr_ranges

    def set_downstream(self, cntrls: list[AbstractController]) -> None:
        self.downstream_destinations = cntrls
