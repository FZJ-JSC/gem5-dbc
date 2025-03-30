from g5dbc.config import Config
from g5dbc.sim.m5_objects.ruby import m5_RubySystem
from g5dbc.sim.model.network import AbstractNetwork
from g5dbc.sim.model.network.garnet import Garnet_Network
from g5dbc.sim.model.network.simple import Simple_Network


class NetworkFactory:

    @staticmethod
    def create(config: Config, ruby_system: m5_RubySystem) -> AbstractNetwork:

        match config.interconnect.model:
            case "garnet":
                return Garnet_Network(
                    config,
                    ruby_system=ruby_system,
                    routers=[],
                    ext_links=[],
                    int_links=[],
                    netifs=[],
                    ni_flit_size=config.interconnect.garnet.data_link_width,
                    vcs_per_vnet=config.interconnect.garnet.vcs_per_vnet,
                    routing_algorithm=config.interconnect.garnet.routing_algorithm,
                    garnet_deadlock_threshold=config.interconnect.garnet.deadlock_threshold,
                    number_of_virtual_networks=config.network.n_vnets,
                    control_msg_size=config.interconnect.garnet.cntrl_msg_size,
                    data_msg_size=config.network.data_width,
                )
            case "simple":
                return Simple_Network(
                    config,
                    ruby_system=ruby_system,
                    routers=[],
                    ext_links=[],
                    int_links=[],
                    netifs=[],
                    number_of_virtual_networks=config.network.n_vnets,
                    control_msg_size=config.interconnect.simple.cntrl_msg_size,
                    data_msg_size=config.network.data_width,
                    buffer_size=config.interconnect.simple.router_buffer_size,
                )
            case _:
                raise ValueError(f"Unknown network {config.interconnect.model}")
