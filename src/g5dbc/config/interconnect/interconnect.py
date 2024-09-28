from dataclasses import dataclass

@dataclass
class Garnet:
    data_width: int = 64
    data_link_width: int = 72
    link_width_bits: int = 576
    vcs_per_vnet: int = 16
    routing_algorithm: int = 0
    deadlock_threshold: int = 500000
    use_link_bridges: bool = False
    cntrl_msg_size: int = 8

    def __post_init__(self):
        self.data_link_width = self.cntrl_msg_size + self.data_width
        self.link_width_bits = self.data_link_width * 8

@dataclass
class Simple:
    data_width: int = 64
    link_bandwidth: int = 64
    cntrl_msg_size: int = 8
    bandwidth_factor: int = 64
    router_buffer_size: int = 4

@dataclass
class InterconnectConf:
    garnet: Garnet
    simple: Simple

    def __post_init__(self):

        if isinstance(self.garnet, dict):
            self.garnet = Garnet(**self.garnet)

        if isinstance(self.simple, dict):
            self.simple = Simple(**self.simple)
