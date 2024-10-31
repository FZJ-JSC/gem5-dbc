from modules.ruby.topology.Mesh_NOC.Mesh_NOC import Mesh_NOC


def create_topology(network_nodes, network_cntrls, options):
    topology = Mesh_NOC(network_nodes)
    
    return topology
