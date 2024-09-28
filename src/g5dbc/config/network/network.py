from dataclasses import dataclass, field, asdict

@dataclass
class TopologyConf:
    model: str
    parameters: dict = field(default_factory=dict)

@dataclass
class NetworkConf:

    mesh_vnet_support: list[list[int]]
    node_vnet_support: list[list[int]]

    data_width: int = 64
    clock:  str = ""
    router_latency: int = 1

    n_vnets: int = 4
    # @TODO:
    xor_low_bit: int = 20

    mesh_link_latency: int = 1
    node_link_latency: int = 1
    cross_numa_latency: int = 1

    topology: dict[str,TopologyConf] = field(default_factory=dict)

    def __post_init__(self):
        for k,v in self.topology.items():
            if isinstance(v, dict):
                self.topology[k] = TopologyConf(**v)
