from g5dbc.config.caches import CacheConf
from g5dbc.sim.m5_objects.cache import m5_L2XBar, m5_SnoopFilter


class ClassicXBar(m5_L2XBar):
    def __init__(self, config: CacheConf, **kwargs):
        super().__init__(**kwargs)
        self.width = config.classic.xbar_width

        if config.classic.snoop_filter_max_capacity is not None:
            self.snoop_filter = m5_SnoopFilter(
                lookup_latency=0,
                max_capacity=config.classic.snoop_filter_max_capacity,
            )
