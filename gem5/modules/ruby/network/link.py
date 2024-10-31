import m5

from modules.options import Options

from modules.util import fatal_error

def create_int_link(options: Options, **kwargs):

    model = options.architecture.NOC.network.model

    link_id  = kwargs["link_id"]
    src_node = kwargs["src_node"]
    dst_node = kwargs["dst_node"]
    vnet_support   = kwargs["vnet_support"]
    latency        = kwargs.get("latency", options.architecture.NOC.topology.mesh_link_latency)
    link_bandwidth = kwargs.get("link_bandwidth", options.architecture.NOC.network.simple.link_bandwidth)

    dst_inport = kwargs.get("dst_inport", "")
    weight     = kwargs.get("weight", 1)

    if model == "garnet":
        link = m5.objects.GarnetIntLink(
                    link_id  = link_id,
                    src_node = src_node,
                    dst_node = dst_node,
                    latency = latency,
                    supported_vnets=vnet_support,
                    dst_inport = dst_inport,
                    weight  = weight
                )

    elif model == "simple":
        link = m5.objects.SimpleIntLink(
                    link_id  = link_id,
                    src_node = src_node,
                    dst_node = dst_node,
                    dst_inport = dst_inport,
                    latency = latency,
                    weight  = weight,
                    supported_vnets  = vnet_support,
                    bandwidth_factor = link_bandwidth
        )
    else:
        fatal_error(f"Unknown network {model}")

    return link



def create_ext_link(options: Options, **kwargs):

    link_id  = kwargs["link_id"]
    ext_node = kwargs["ext_node"]
    int_node = kwargs["int_node"]
    latency  = kwargs["latency"]
    vnet_support  = kwargs["vnet_support"]
    bandwidth_factor = kwargs.get("bandwidth_factor",1)

    if options.architecture.NOC.network.model == "garnet":
        link = m5.objects.GarnetExtLink(
                link_id = link_id,
                ext_node = ext_node,
                int_node = int_node,
                latency = latency,
                supported_vnets=vnet_support
                )

    elif options.architecture.NOC.network.model == "simple":
        link = m5.objects.SimpleExtLink(
                link_id  = link_id,
                ext_node = ext_node,
                int_node = int_node,
                latency  = latency,
                supported_vnets=vnet_support,
                bandwidth_factor = bandwidth_factor
                )
    else:
        fatal_error(f"Unknown network {options.architecture.NOC.network.model}")

    return link
