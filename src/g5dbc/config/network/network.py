from dataclasses import asdict, dataclass, field


@dataclass
class TopologyConf:
    model: str = ""
    parameters: dict = field(default_factory=dict)


@dataclass
class NetworkConf:
    topology: TopologyConf = field(default_factory=TopologyConf)
    mesh_vnet_support: list[list[int]] = field(default_factory=list)
    node_vnet_support: list[list[int]] = field(default_factory=list)
    clock: str = ""
    data_width: int = 64
    router_latency: int = 1
    n_vnets: int = 4
    # @TODO:
    xor_low_bit: int = 20
    mesh_link_latency: int = 1
    node_link_latency: int = 1
    cross_numa_latency: int = 1

    def __post_init__(self):
        if isinstance(self.topology, dict):
            self.topology = TopologyConf(**self.topology)
        if not self.mesh_vnet_support:
            self.mesh_vnet_support = [[n for n in range(self.n_vnets)]]
        if not self.node_vnet_support:
            self.node_vnet_support = [[n for n in range(self.n_vnets)]]
