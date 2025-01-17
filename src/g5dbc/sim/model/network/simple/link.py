from g5dbc.sim.m5_objects.ruby.network import m5_SimpleExtLink, m5_SimpleIntLink

from ...network.NetworkLink import NetworkLink


class Simple_IntLink(m5_SimpleIntLink, NetworkLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Simple_ExtLink(m5_SimpleExtLink, NetworkLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
