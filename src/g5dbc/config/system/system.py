from dataclasses import dataclass, field, asdict

@dataclass
class SystemConf:
    architecture: str = "arm64"
    num_cpus: int = 16
    clock:     str = "2.6GHz"
    cpu_clock: str = ""
    voltage: str = "1.0V"
    platform: str = "VExpress_GEM5_V2"
    interconnect: str | None = "garnet"
    topology: str = "Simple2D"
    cache_line_size: int = 64
    sve_vl: int = 256
    cpus: list[str] = field(default_factory=list)

    fs_mode: bool = True

    def activeNOC(self) -> bool:
        return self.interconnect is not None
    
    def __post_init__(self):
        if self.cpu_clock == "":
            self.cpu_clock = self.clock
