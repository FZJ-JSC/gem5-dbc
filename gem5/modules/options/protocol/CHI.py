
class CHI_NODE:
    def __init__(self,parameters,link_latency=0):
        self.router_list = parameters["routers"]
        self.nodes_per_router = parameters["nodes_per_router"] if 'nodes_per_router' in parameters else None
        self.link_latency = parameters["link_latency"] if 'link_latency' in parameters else link_latency
        self.extra_inbound_latency = 0
        self.extra_outbound_latency = 0

class Options:
    def __init__(self,parameters, num_cpus=0, num_slcs=0, link_latency=0):
        self.nodes = dict()

        self.rnf_single_router = parameters["nodes"]["RNF"]["single_router"]
        
        for key, params in parameters["nodes"].items():
            self.nodes[key] = CHI_NODE(params, link_latency=link_latency)

        assert(num_cpus >= len(self.nodes["RNF"].router_list))
        assert(num_slcs >= len(self.nodes["HNF"].router_list))

        # Set nodes_per_router        
        self.nodes["RNF"].nodes_per_router = num_cpus // len(self.nodes["RNF"].router_list)
        self.nodes["HNF"].nodes_per_router = num_slcs // len(self.nodes["HNF"].router_list)

        self.pairing = None
        if 'pairing' in []:
            self.pairing = self.nodes['CHI_HNF']['pairing']
