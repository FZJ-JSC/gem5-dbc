from g5dbc.config.caches import CacheConf, PrefetcherConf
from g5dbc.sim.factory.prefetcher import PrefetcherFactory
from g5dbc.sim.m5_objects.cache import m5_Cache


class ClassicCache(m5_Cache):
    def __init__(self, config: CacheConf, **kwargs):
        _attr = dict(**kwargs)
        for k, v in config.extra_parameters.items():
            if hasattr(m5_Cache, k):
                _attr[k] = v
        super().__init__(**_attr)

        self.size = config.size
        self.assoc = config.assoc
        self.tag_latency = config.latency.tag
        self.data_latency = config.latency.data
        self.response_latency = config.latency.response
        self.mshrs = config.classic.mshrs
        self.tgts_per_mshr = config.classic.tgts_per_mshr
        self.write_buffers = config.classic.write_buffers
        self.writeback_clean = config.classic.writeback_clean

    def set_prefetcher(self, config: PrefetcherConf | None):
        if config is not None:
            self.prefetcher = PrefetcherFactory.create(config)
