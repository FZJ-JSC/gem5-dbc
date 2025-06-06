from g5dbc.sim.m5_objects.ruby.network import m5_Switch

from ...network.NetworkRouter import NetworkRouter


class Simple_Router(m5_Switch, NetworkRouter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
