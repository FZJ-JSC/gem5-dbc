from g5dbc.config.caches import CacheConf
from g5dbc.sim.m5_objects.cache import m5_Cache


class ClassicCache(m5_Cache):
    def __init__(self, config: CacheConf, **kwargs):
        super().__init__(**kwargs)
        self.size = config.size
        self.assoc = config.assoc
        self.tag_latency = config.latency.tag
        self.data_latency = config.latency.data
        self.response_latency = config.latency.response

        self.mshrs = config.classic.mshrs
        self.tgts_per_mshr = config.classic.tgts_per_mshr
        self.write_buffers = config.classic.write_buffers
        self.writeback_clean = config.classic.writeback_clean
