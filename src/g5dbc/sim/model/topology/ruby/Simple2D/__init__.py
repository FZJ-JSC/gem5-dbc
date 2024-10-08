from dataclasses import dataclass

from g5dbc.config import Config
from ...spec import NodeType, RouterSpec, LinkSpec
from ..RubyTopology import RubyTopology

@dataclass
class Options:
    num_mesh_routers: int
    router_numa_ids :list[int]
    cpu_routers: list[list[int]]
    slc_routers: list[list[int]]
    mem_routers: list[list[int]]
    rom_routers: list[int]
    dma_routers: list[int]
    internal_links:list[list[int]]


class Simple2D(RubyTopology):

    def __init__(self, config: Config):
        assert config.network.topology[config.system.topology].model == "Simple2D"
        params = config.network.topology[config.system.topology].parameters

        self.config_topo = Options(**params)

        self._num_cpus = config.system.num_cpus
        self._mem_regions  = config.memory.regions
        self._link_latency = config.network.mesh_link_latency
        self._numa_latency = config.network.cross_numa_latency

    def get_routers(self, node_type: NodeType) -> list[RouterSpec]:
        match node_type:
            case NodeType.CPU:
                return self.get_cpu_routers()
            case NodeType.SLC:
                return self.get_slc_routers()
            case NodeType.MEM:
                return self.get_mem_routers()
            case NodeType.ROM:
                return self.get_rom_routers()
            case NodeType.DMA:
                return self.get_dma_routers()
            case _:
                raise ValueError(f"Unknown node type {node_type}")

    def num_mesh_routers(self) -> int:
        config_topo = self.config_topo

        return config_topo.num_mesh_routers
    
    def get_router_numa_ids(self) -> list[int]:
        config_topo = self.config_topo
   
        return config_topo.router_numa_ids


    def get_cpu_routers(self) -> list[RouterSpec]:
        config_topo = self.config_topo

        routers = config_topo.cpu_routers
        nodes_per_router = self._num_cpus // len(sum(routers, []))
        
        specs = [RouterSpec(router_ids, numa_id=numa_id, nodes_per_router=nodes_per_router) for numa_id,router_ids in enumerate(routers)]
        
        return specs


    def get_slc_routers(self) -> list[RouterSpec]:
        config_topo = self.config_topo

        routers = config_topo.slc_routers
        nodes_per_router = 1

        specs = [RouterSpec(router_ids, numa_id=numa_id, nodes_per_router=nodes_per_router) for numa_id,router_ids in enumerate(routers)]
        
        return specs

    def get_mem_routers(self) -> list[RouterSpec]:
        """
        Return a map region name -> list of routers
        """
        config_topo = self.config_topo
        mem_regions = self._mem_regions

        routers = config_topo.mem_routers
        nodes_per_router = [region.channels // len(routers[numa_id]) for numa_id,region in enumerate(mem_regions)]

        assert len(routers) == len(mem_regions), f"Number of memory regions {len(mem_regions)} does not match topology {len(routers)}"
        assert min(nodes_per_router) > 0, "Not enough memory channels for given topology"

        specs = [RouterSpec(router_ids=router_ids, numa_id=numa_id, nodes_per_router=nodes_per_router[numa_id]) for numa_id,router_ids in enumerate(routers)]

        return specs


    def get_rom_routers(self) -> RouterSpec:
        config_topo = self.config_topo
        router_ids = config_topo.rom_routers
        routers = RouterSpec(router_ids=router_ids)
        return routers

    def get_dma_routers(self) -> RouterSpec:
        config_topo = self.config_topo
        router_ids = config_topo.dma_routers
        routers = RouterSpec(router_ids=router_ids)
        return routers

    def mesh_links(self) -> list[LinkSpec]:
        config_topo = self.config_topo

        router_numa_ids    = self.get_router_numa_ids()
        mesh_link_latency  = self._link_latency
        cross_numa_latency = self._numa_latency
        internal_links: list[LinkSpec] = []

        for l in config_topo.internal_links:
            src = l[0]
            dst = l[1]
            weight = l[2]
            lat = mesh_link_latency if router_numa_ids[src] == router_numa_ids[dst] else cross_numa_latency
            # Override latency if given explicitly
            if len(l) > 3:
                lat = l[3]
            internal_links.append(LinkSpec(src=src,dst=dst,latency=lat,weight=weight))
            internal_links.append(LinkSpec(src=dst,dst=src,latency=lat,weight=weight))

        return internal_links


    def mesh_links2(self) -> list[LinkSpec]:
        config_topo = self.config_topo

        num_cols = 3
        num_rows = 2

        router_numa_ids = self.get_router_numa_ids()
        mesh_link_latency  = self._link_latency
        cross_numa_latency = self._numa_latency
        internal_links: list[LinkSpec] = []

        # X Links
        for row in range(num_rows):
            for col in range(num_cols - 1):
                src = col + (row * num_cols)
                dst = (col + 1) + (row * num_cols)
                lat = mesh_link_latency if router_numa_ids[src] == router_numa_ids[dst] else cross_numa_latency
                internal_links.append(LinkSpec(src=src,dst=dst,latency=lat,weight=1))
                internal_links.append(LinkSpec(src=dst,dst=src,latency=lat,weight=1))

        for row in range(num_rows-1):
            for col in range(num_cols):
                src = col + (row * num_cols)
                dst = col + ((row + 1) * num_cols)
                lat = mesh_link_latency if router_numa_ids[src] == router_numa_ids[dst] else cross_numa_latency
                internal_links.append(LinkSpec(src=src,dst=dst,latency=lat,weight=2))
                internal_links.append(LinkSpec(src=dst,dst=src,latency=lat,weight=2))

        return internal_links
