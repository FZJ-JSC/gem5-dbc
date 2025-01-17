from g5dbc.sim.m5_objects.ruby.network import m5_Switch

from ...network.NetworkRouter import NetworkRouter


class Simple_Router(NetworkRouter, m5_Switch):
    def __init__(self, **kwargs):
        m5_Switch.__init__(**kwargs)
