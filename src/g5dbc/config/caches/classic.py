from dataclasses import dataclass


@dataclass
class ClassicCacheConf:
    mshrs: int = 96
    tgts_per_mshr: int = 16
    write_buffers: int = 24
    writeback_clean: bool = False
    xbar_width: int | None = None
    bus_width: int | None = None
    clusivity: str = "mostly_incl"
    snoop_filter_max_capacity: str | None = None
