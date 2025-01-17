from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby.network import m5_SimpleNetwork

from ...network.AbstractNetwork import AbstractNetwork
from ...network.NetworkLink import NetworkLink
from ...network.NetworkRouter import NetworkRouter


class Simple_Network(AbstractNetwork, m5_SimpleNetwork):

    def __init__(self, config: Config, **kwargs):
        m5_SimpleNetwork.__init__(self, **kwargs)

        self._config = config

    def initialize(self) -> None:
        self.network.setup_buffers()

    def set_routers(self, routers: list[NetworkRouter]) -> None:
        self.routers = routers

    def set_int_links(self, links: list[NetworkLink]) -> None:
        self.int_links = links

    def set_ext_links(self, links: list[NetworkLink]) -> None:
        self.ext_links = links
