from g5dbc.config.caches import CacheConf, PrefetcherConf
from g5dbc.sim.m5_objects.ruby import m5_RubyCache


class Ruby_Cache(m5_RubyCache):
    def __init__(self, config: CacheConf):
        _attr = dict()
        for k, v in config.extra_parameters.items():
            if hasattr(m5_RubyCache, k):
                _attr[k] = v
        super().__init__(**_attr)

        self.size = config.size
        self.assoc = config.assoc
        self.dataAccessLatency = config.latency.data
        self.tagAccessLatency = config.latency.tag
        self.start_index_bit = config.block_size_bits
        self.resourceStalls = config.resource_stalls
        self.is_icache = config.is_icache()
