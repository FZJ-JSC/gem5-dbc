from g5dbc.sim.m5_objects.ruby.network import m5_GarnetIntLink, m5_GarnetExtLink

from ...network.NetworkLink import NetworkLink

class Garnet_IntLink(m5_GarnetIntLink, NetworkLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Garnet_ExtLink(m5_GarnetExtLink, NetworkLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
