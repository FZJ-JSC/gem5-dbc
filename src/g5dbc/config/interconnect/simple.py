from dataclasses import dataclass


@dataclass
class Simple:
    data_width: int = 64
    link_bandwidth: int = 64
    cntrl_msg_size: int = 8
    bandwidth_factor: int = 64
    router_buffer_size: int = 4
