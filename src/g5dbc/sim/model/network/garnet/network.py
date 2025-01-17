from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby.network import (
    m5_GarnetNetwork,
    m5_GarnetNetworkInterface,
)
from g5dbc.sim.model.interconnect.ruby.node import AbstractNode
from g5dbc.sim.model.topology import AbstractTopology
from g5dbc.sim.model.topology.spec import LinkSpec, NodeSpec, RouterSpec

from ...network.AbstractNetwork import AbstractNetwork
from ...network.NetworkLink import NetworkLink
from ...network.NetworkRouter import NetworkRouter
from .link import Garnet_ExtLink, Garnet_IntLink
from .router import Garnet_Router


class Garnet_Network(m5_GarnetNetwork, AbstractNetwork):

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self._config = config

        self._use_link_bridges = False
        self._num_links = 0

        self._routers: list[NetworkRouter] = []
        self._int_links: list[NetworkLink] = []
        self._ext_links: list[NetworkLink] = []

    def initialize(self, topology: AbstractTopology) -> list[NetworkRouter]:
        """
        Create network routers based on topology
        """
        config = self._config
        mesh_lvs = config.network.mesh_vnet_support
        router_latency = config.network.router_latency

        # Create mesh routers
        for i in range(topology.num_mesh_routers()):
            self.create_router(latency=router_latency)

        for link in topology.mesh_links():
            for vnets in mesh_lvs:
                self.create_link(link, vnets)

    def connect_interfaces(self):
        self.int_links = self._int_links
        self.ext_links = self._ext_links
        self.routers = self._routers
        self.netifs = [
            m5_GarnetNetworkInterface(id=i) for (i, link) in enumerate(self._ext_links)
        ]

    def connect_nodes(self, nodes: list[AbstractNode]):
        config = self._config
        mesh_lvs = config.network.mesh_vnet_support

        for node in nodes:
            if node.needs_exclusive_router():
                router = self.attach_exclusive_router(node.get_router_id())
                node.set_router_id(router.get_router_id())

        for node in nodes:
            # for vnets in mesh_lvs:
            self.connect_node(node, mesh_lvs)

    def attach_exclusive_router(self, mesh_router_id: int) -> NetworkRouter:
        config = self._config

        node_vnet_support = config.network.node_vnet_support
        link_latency = config.network.mesh_link_latency
        router_latency = config.network.router_latency

        router = self.create_router(latency=router_latency)

        src_id = router.get_router_id()
        dst_id = mesh_router_id

        network_links = [
            LinkSpec(src=src_id, dst=dst_id, latency=link_latency),
            LinkSpec(src=dst_id, dst=src_id, latency=link_latency),
        ]

        for link in network_links:
            for vnets in node_vnet_support:
                self.create_link(link, vnets)

        return router

    def create_router(self, **kwargs) -> NetworkRouter:
        routers = self._routers
        router_id = len(routers)
        router = Garnet_Router(router_id=router_id, **kwargs)
        routers.append(router)

        return router

    def create_link(self, link: LinkSpec, vnets: list[int]):
        routers = self._routers
        int_links = self._int_links

        link_id = len(int_links)
        int_links.append(
            Garnet_IntLink(
                link_id=link_id,
                src_node=routers[link.src],
                dst_node=routers[link.dst],
                latency=link.latency,
                supported_vnets=vnets,
                weight=link.weight,
            )
        )

    def connect_node(self, node: AbstractNode, mesh_lvs: list[list[int]]):
        config = self._config
        routers = self._routers
        int_links = self._int_links
        ext_links = self._ext_links

        link_latency = config.network.node_link_latency

        router = routers[node.get_router_id()]
        for ctrl in node.get_controllers():
            for vnets in mesh_lvs:
                link_id = len(int_links) + len(ext_links)
                ext_links.append(
                    Garnet_ExtLink(
                        link_id=link_id,
                        ext_node=ctrl,
                        int_node=router,
                        latency=link_latency,
                        supported_vnets=vnets,
                    )
                )

            ctrl.connect_network(self)
