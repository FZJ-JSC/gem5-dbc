from dataclasses import dataclass


@dataclass
class ClassicCacheConf:
    mshrs: int = 16
    tgts_per_mshr: int = 16
    write_buffers: int = 8
    writeback_clean: bool = False
    xbar_width: int = 64
    clusivity: str = "mostly_incl"
    snoop_filter_max_capacity: str | None = None
