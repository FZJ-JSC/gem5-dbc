from dataclasses import asdict, dataclass, field


@dataclass
class SystemConf:
    architecture: str = "arm64"
    num_cpus: int = 16
    num_slcs: int = 16
    clock: str = "2.6GHz"
    voltage: str = "1.0V"
    platform: str = "VExpress_GEM5_V2"
    cache_line_size: int = 64
    sve_vl: int = 256
    cpus: list[str] = field(default_factory=list)
