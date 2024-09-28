from abc import ABC, abstractmethod

from .spec import NodeSpec, NodeType, LinkSpec

class AbstractTopology(ABC):
    """
    Abstract Topology
    """

    @abstractmethod
    def num_mesh_routers(self) -> int:
        """
        Get the total number of internal mesh routers
        """

    @abstractmethod
    def mesh_links(self) -> list[LinkSpec]:
        """
        Get a list of internal mesh links
        """

    @abstractmethod
    def get_nodes(self, node_type: NodeType) -> list[NodeSpec]:
        """
        Return a list of node_type nodes
        """
