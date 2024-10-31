import re

from modules.stats.parsers import util


__max_vcs = 4

def parse_ruby_network(key:str, val: str, r: dict):

    # Average Flit/Packet latency
    p = r"system\.ruby\.network\.average_(flit|packet)_?(network|queueing)?_latency"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        source = m.group(2) if m.group(2) else 'all'
        r = util.accumulate_num_col(f"network_average_{name}_{source}_latency", val, r)
        return r

    p = r"system\.ruby\.network\.(average_hops|avg_link_utilization)"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        r = util.accumulate_num_col(f"network_{name}", val, r)
        return r

    p = r"system\.ruby\.network\.(avg_vc_load|flits_injected|flits_received)::total"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        r = util.accumulate_num_col(f"network_{name}_total", val, r)
        return r

    p = r"system\.ruby\.network\.(ext_in|ext_out|int)_link_utilization"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        r = util.accumulate_num_col(f"network_{name}_link_utilization", val, r)
        return r

    p = r"system\.ruby\.network\.(total|router)_(hops)$"
    m = re.match(p, key)
    if m:
        zone = "mesh" if m.group(1) == "router" else "network"
        name = m.group(2)
        r = util.accumulate_num_col(f"{zone}_total_{name}", val, r)
        return r

    p = r"system\.ruby\.network\.avg_vc_load$"
    m = re.match(p, key)
    if m:
        hist = {"network_avg_vc_load_vnet{}_vc{}".format(k//__max_vcs, k%__max_vcs): float(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    p = r"system\.ruby\.network\.average_(flit|packet)_(vnet|vqueue)_latency$"
    m = re.match(p, key)
    if m:
        flit = m.group(1)
        netw = m.group(2)
        hist = {f"network_average_{flit}_{netw}_latency_vnet{k}": float(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    p = r"system\.ruby\.network\.(router)?_?(flit|packet)_(network|queueing)_latency$"
    m = re.match(p, key)
    if m:
        zone = "mesh" if m.group(1) else "network"
        flit = m.group(2)
        netw = m.group(3)
        hist = {f"{zone}_{flit}_{netw}_latency_vnet{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    p = r"system\.ruby\.network\.(router)?_?(flits|packets)_(injected|received)$"
    m = re.match(p, key)
    if m:
        zone = "mesh" if m.group(1) else "network"
        flit = m.group(2)
        recv = m.group(3)
        hist = {f"{zone}_{flit}_{recv}_vnet{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    # Network hops histogram
    p = r"system\.ruby\.network\.(router_hops_hist)_vnet(\d+)$"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        vnet = m.group(2)
        hist = {f"mesh_{name}_vnet{vnet}_{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r
    
    # Network traffic
    p = r"system\.ruby\.network\.(routers|net_ifs)_vnet(\d+)_src_dst$"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        vnet = m.group(2)
        hist = {f"network_{name}_vnet{vnet}_src_dst_{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    return r
