from abc import ABC, abstractmethod
from typing import Callable

from ..spec import NodeType, NodeSpec, RouterSpec
from ..AbstractTopology import AbstractTopology

class RubyTopology(AbstractTopology):
    """
    Ruby Topology
    """

    @abstractmethod
    def get_router_numa_ids(self) -> list[int]:
        """
        Get a map router_id -> numa_id
        """

    @abstractmethod
    def get_routers(self, node_type: NodeType) -> list[RouterSpec]:
        """
        """

    def get_nodes(self, node_type: NodeType) -> list[NodeSpec]:
        match node_type:
            case NodeType.CPU:
                return self.get_cpu_nodes()
            case NodeType.SLC:
                return self.get_slc_nodes()
            case NodeType.MEM:
                return self.get_mem_nodes()
            case NodeType.ROM:
                return self.get_rom_nodes()
            case NodeType.DMA:
                return self.get_dma_nodes()
            case _:
                raise ValueError(f"Unknown node type {node_type}")

    def get_cpu_nodes(self) -> list[NodeSpec]:
        specs = self.get_routers(NodeType.CPU)
        idmap = lambda idx, spec: spec.router_ids[idx // spec.nodes_per_router]
        nodes = self.get_ctrl_nodes(idmap, specs)

        for core_id, node_id in enumerate(nodes):
            node_id.core_id = core_id
            node_id.needs_exclusive_router = True

        return nodes

    def get_slc_nodes(self) -> list[NodeSpec]:
        specs = self.get_routers(NodeType.SLC)
        idmap = lambda idx, spec: spec.router_ids[idx % len(spec.router_ids)]
        nodes = self.get_ctrl_nodes(idmap, specs)
        return nodes

    def get_mem_nodes(self) -> list[NodeSpec]:
        specs = self.get_routers(NodeType.MEM)
        idmap = lambda idx, spec: spec.router_ids[idx % len(spec.router_ids)]
        nodes = self.get_ctrl_nodes(idmap, specs)
        return nodes

    def get_rom_nodes(self) -> list[NodeSpec]:
        specs = self.get_routers(NodeType.ROM)
        nodes = [NodeSpec(router_id=router_id) for router_id in specs.router_ids]
        return nodes
    
    def get_dma_nodes(self) -> list[NodeSpec]:
        specs = self.get_routers(NodeType.DMA)
        nodes = [NodeSpec(router_id=router_id) for router_id in specs.router_ids]
        return nodes

    def get_ctrl_nodes(self, id_map: Callable[[int,RouterSpec], int], specs: list[RouterSpec]) -> list[NodeSpec]:
        numa_ids = self.get_router_numa_ids()
        nodes : list[NodeSpec] = []
        for numa_id,spec in enumerate(specs):
            for ctrl_id in range(spec.num_ctrls()):
                router_id = id_map(ctrl_id, spec)
                assert numa_id == numa_ids[router_id], f"router_id={router_id} numa_id={numa_id} numa_ids={numa_ids}"
                nodes.append(NodeSpec(ctrl_id=ctrl_id,router_id=router_id,numa_id=numa_id))

        nodes.sort()
        
        return nodes
