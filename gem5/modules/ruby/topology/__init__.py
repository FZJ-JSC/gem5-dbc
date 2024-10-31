import importlib

from modules.ruby.topology.Simple import SimpleTopology


def create_topology(network_nodes, network_cntrls, options):
    topology_name = options.architecture.NOC.topology.model
    Topo = importlib.import_module(f"modules.ruby.topology.{topology_name}")
    topology = Topo.create_topology(network_nodes, network_cntrls, options)

    return topology
