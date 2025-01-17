from g5dbc.sim.m5_objects.ruby.network import m5_GarnetRouter

from ...network.NetworkRouter import NetworkRouter


class Garnet_Router(m5_GarnetRouter, NetworkRouter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_router_id(self) -> int:
        return self.router_id.value
