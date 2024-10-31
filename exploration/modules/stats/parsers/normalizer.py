
import math
import numpy as np
import re

__num_vnets = 4


def rate_or_zero(a,b):
    if b == 0:
        return 0.0
    else:
        return float(a)/float(b)


def normalize_clocks(r:dict):
    r['time']    = float(r['simTicks'])/r['simFreq']
    r['cycles']  = float(r['simTicks'])/r['cpu_clock']

    return r

def normalize_ruby_caches(r: dict):
    r['dcache_accesses'] = r.get('caches_l1d_demand_accesses',0)
    r['dcache_hits']     = r.get('caches_l1d_demand_hits',0)
    r['dcache_misses']   = r.get('caches_l1d_demand_misses',0)

    r['icache_accesses'] = r.get('caches_l1i_demand_accesses',0)
    r['icache_hits']     = r.get('caches_l1_demand_hits',0)
    r['icache_misses']   = r.get('caches_l1i_demand_misses',0)

    r['l2_demand_accesses'] = r.get('caches_l2_demand_accesses',0)
    r['l2_demand_hits']     = r.get('caches_l2_demand_hits',0)
    r['l2_demand_misses']   = r.get('caches_l2_demand_misses',0)

    r['l3_demand_accesses'] = r.get('HNF_demand_accesses',0)
    r['l3_demand_hits']     = r.get('HNF_demand_hits',0)
    r['l3_demand_misses']   = r.get('HNF_demand_misses',0)

    r['l2_prefetch_accesses'] = r.get('caches_l2_prefetch_accesses',0)
    r['l2_prefetch_hits']     = r.get('caches_l2_prefetch_hits',0)
    r['l2_prefetch_misses']   = r.get('caches_l2_prefetch_misses',0)

    r['l3_prefetch_accesses'] = r.get('HNF_prefetch_accesses',0)
    r['l3_prefetch_hits']     = r.get('HNF_prefetch_hits',0)
    r['l3_prefetch_misses']   = r.get('HNF_prefetch_misses',0)

    return r


def normalize_ruby_network(r: dict):
    cycles = r['cycles']
    ruby_clock = r['ruby_clock']

    r['network_ext_link_utilization']   = r.get('network_ext_in_link_utilization',0) + r.get('network_ext_out_link_utilization',0)

    r['network_avg_int_link_util'] = float(r.get('network_int_link_utilization',0)) / cycles
    r['network_avg_ext_link_util'] = float(r.get('network_ext_link_utilization',0)) / cycles
    r['network_avg_ext_in_link_util'] = float(r.get('network_ext_in_link_utilization',0)) / cycles
    r['network_avg_ext_out_link_util'] = float(r.get('network_ext_out_link_utilization',0)) / cycles


    # total traffic
    r['network_avg_packet_latency']           = float(r.get('network_average_packet_all_latency',0)) / ruby_clock
    r['network_avg_packet_latency_network']   = float(r.get('network_average_packet_network_latency',0)) / ruby_clock
    r['network_avg_packet_latency_queueing']  = float(r.get('network_average_packet_queueing_latency',0)) / ruby_clock

    for vnet in range(__num_vnets):
        r[f'network_avg_packet_latency_network_vnet{vnet}']  = float(r.get(f'network_average_packet_vnet_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_avg_packet_latency_queueing_vnet{vnet}'] = float(r.get(f'network_average_packet_vqueue_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_avg_packet_latency_vnet{vnet}'] = r[f'network_avg_packet_latency_network_vnet{vnet}'] + r[f'network_avg_packet_latency_queueing_vnet{vnet}']

        r[f'network_packet_latency_network_vnet{vnet}']  = float(r.get(f'network_packet_network_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_packet_latency_queueing_vnet{vnet}'] = float(r.get(f'network_packet_queueing_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_packet_latency_vnet{vnet}']     = r[f'network_packet_latency_network_vnet{vnet}'] + r[f'network_packet_latency_queueing_vnet{vnet}']

        r[f'network_avg_flit_latency_network_vnet{vnet}']    = float(r.get(f'network_average_flit_vnet_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_avg_flit_latency_queueing_vnet{vnet}']   = float(r.get(f'network_average_flit_vqueue_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_flit_latency_network_vnet{vnet}']    = float(r.get(f'network_flit_network_latency_vnet{vnet}',0)) / ruby_clock
        r[f'network_flit_latency_queueing_vnet{vnet}']   = float(r.get(f'network_flit_queueing_latency_vnet{vnet}',0)) / ruby_clock


    # mesh traffic
    for p in ["packet", "flit"]:
        r[f"mesh_{p}_latency_total"]    = 0
        r[f"mesh_{p}s_received_total"]  = 0
        for q in ["network", "queueing"]:
            r[f"mesh_{p}_latency_{q}"]  = 0
        for vnet in range(__num_vnets):
            r[f"mesh_avg_{p}_latency_total_vnet{vnet}"] = 0

        for vnet in range(__num_vnets):
            recv = r.get(f"mesh_{p}s_received_vnet{vnet}",0)

            r[f"mesh_{p}s_received_total"]  += recv
            for q in ["network", "queueing"]:
                latency = float(r[f"mesh_{p}_{q}_latency_vnet{vnet}"]) / ruby_clock
                r[f"mesh_{p}_latency_{q}"] += latency
                r[f"mesh_avg_{p}_latency_{q}_vnet{vnet}"] = (latency / recv) if recv != 0 else np.NaN
                r[f"mesh_avg_{p}_latency_total_vnet{vnet}"] += (latency / recv) if recv != 0 else np.NaN
        
        recv = r[f"mesh_{p}s_received_total"]
        r[f"mesh_{p}_latency_total"] = r[f"mesh_{p}_latency_network"] + r[f"mesh_{p}_latency_queueing"]
        r[f"mesh_avg_{p}_latency_network"]  = float(r[f"mesh_{p}_latency_network"])  / recv  if recv != 0 else np.NaN
        r[f"mesh_avg_{p}_latency_queueing"] = float(r[f"mesh_{p}_latency_queueing"]) / recv  if recv != 0 else np.NaN
        r[f"mesh_avg_{p}_latency_total"]    = float(r[f"mesh_{p}_latency_total"])    / recv  if recv != 0 else np.NaN

    r['network_total_hops_cycle']     = float(r.get('network_average_hops',0) * r.get('network_flits_received_total',0)) / cycles
    r['network_flits_received_cycle'] = float(r.get('network_flits_received_total',0) ) / cycles

    recv =  r["mesh_flits_received_total"]
    r["mesh_total_hops"]           = r.get("mesh_total_hops",0)
    r["mesh_total_hops_cycle"]     = float(r["mesh_total_hops"]) / cycles
    r["mesh_flits_received_cycle"] = float(r["mesh_flits_received_total"] ) / cycles
    r["mesh_average_hops"]         = r["mesh_total_hops"] / recv if recv != 0 else np.NaN

    return r


def normalize_ruby_traffic(r: dict):

    vnets = [ f"network_routers_vnet{i}_src_dst" for i in range(__num_vnets) ]

    for vnet in vnets:
        # select vnet columns
        cols = [c for c in r if re.match(vnet, c)]
        if len(cols) == 0:
            continue
        # construct array from row
        vals = np.array([r[c] for c in cols])
        # determine number of columns
        first_nan = np.argmax(np.isnan(vals[0]))
        ncols = first_nan if first_nan > 0 else len(vals)
        data = vals[:ncols]

        data_external = data.copy() #np.zeros_like(data)
        data_internal = np.zeros_like(data)

        num_elems = math.isqrt(ncols)
        
        for i in range(num_elems):
            data_external[i + i*num_elems] = 0.0
            data_internal[i + i*num_elems] = data[i + i*num_elems]

        total_all = data.sum()
        total_ext = data_external.sum()
        total_int = data_internal.sum()

        r[f"{vnet}_total_packets_all"] = total_all

        r[f"{vnet}_total_packets_ext"] = total_ext
        r[f"{vnet}_total_packets_int"] = total_int

        r[f"{vnet}_total_packets_ext_pc"] = float(total_ext) / total_all
        r[f"{vnet}_total_packets_int_pc"] = float(total_int) / total_all

    return r


def normalize_ruby_routers(r: dict):
    cycles = r['cycles']
    flit_size_bytes = r['flit_size_bytes']

    regex = r"network_router(\d+)_(reads|writes)"

    cols = [c for c in r if re.match(regex, c)]

    for c in cols:
        r[f"{c}_flits"] = float(r[c])
        r[f"{c}_bytes"] = float(r[c]) * flit_size_bytes
        r[f"{c}_flits_per_cycle"] = float(r[c]) / cycles
        r[f"{c}_bytes_per_cycle"] = float(r[c]) * flit_size_bytes / cycles

    return r


def normalize_ruby(r: dict):

    r = normalize_ruby_caches(r)
    r = normalize_ruby_network(r)
    r = normalize_ruby_traffic(r)
    r = normalize_ruby_routers(r)

    return r

def normalize_cpu(r: dict):
    # @TODO
    max_flops_cycle = 4*r['sve_vl']/64

    r['max_flops_cycle'] = max_flops_cycle

    r['CI_FLOPS_cycle']  = float(r['CI_FLOPS'])/r['cycles']

    r['flops_cycle_pc'] = r['CI_FLOPS_cycle'] / max_flops_cycle / r['num_threads']

    r['FU_Int_cycle'] = float(r['FU_Int'])/r['cycles']
    r['FU_Float_cycle']  = float(r['FU_Float'])/r['cycles']
    r['FU_Simd_cycle']  = float(r['FU_Simd'])/r['cycles']
    r['FU_FloatSimd_cycle']  = float(r['FU_FloatSimd'])/r['cycles']
    r['FU_Mem_cycle']  = float(r['FU_Mem'])/r['cycles']

    r['CommittedInsts_cycle'] = float(r['CPU_COMMIT_instsCommitted']) / r['cycles']

    r['CPU_fetch_rate_cpu'] = float(r.get('CPU_FETCH_rate',0)) / r['num_cpus']
    r['CPU_fetch_cycles_rate'] = float(r.get('CPU_FETCH_cycles',0)) /r['cycles']
    r['CPU_fetch_cycles_cpu'] = float(r.get('CPU_FETCH_cycles',0)) #/ r['num_cpus']
    r['CPU_fetch_icacheStallCycles_cpu'] = float(r.get('CPU_FETCH_icacheStallCycles',0)) / r['num_cpus']
    r['CPU_fetch_pendingQuiesceStallCycles_cpu'] = float(r.get('CPU_FETCH_pendingQuiesceStallCycles',0)) / r['num_cpus']

    return r

def normalize_memory(r: dict):

    num_ctrls = r['num_mem_ctrls']

    r['mem_peakBW']    = r.get('mem_ctrls_peakBW',0)

    r['mem_ctrls_bytes_read']    = r.get('mem_ctrls_bytesRead',0)
    r['mem_ctrls_bytes_written'] = r.get('mem_ctrls_bytesWritten',0)

    r['mem_bus_rw_util']    = float(r.get('mem_ctrls_busUtil',0))/ num_ctrls / 100.0
    r['mem_bus_read_util']  = float(r.get('mem_ctrls_busUtilRead',0)) /num_ctrls / 100.0
    r['mem_bus_write_util'] = float(r.get('mem_ctrls_busUtilWrite',0)) / num_ctrls / 100.0

    r['mem_ctrls_bytes_rw']      = r['mem_ctrls_bytes_read']+r['mem_ctrls_bytes_written']
    r['mem_ctrls_read_cycle']    = r['mem_ctrls_bytes_read']/r['cycles']
    r['mem_ctrls_written_cycle'] = r['mem_ctrls_bytes_written']/r['cycles']

    r['bw_bytes_cycle']     = r['mem_ctrls_read_cycle']+r['mem_ctrls_written_cycle']
    r['bw_gem5_GB']  = float(r.get('mem_ctrls_bwTotal',0))/(1e9)

    flops = float(r['CI_FLOPS'])
    data  = float(r['mem_ctrls_bytes_rw'])
    r['FLOPS_Bytes'] = np.Inf
    r['Bytes_FLOPS'] = np.Inf
    if data  > 0:
        r['FLOPS_Bytes'] = flops/data
    if flops > 0:
        r['Bytes_FLOPS'] = data/flops

    return r

def normalize_caches(r: dict):
    r['dcache_accesses'] = r.get('dcache_accesses',0)
    r['dcache_hits']     = r.get('dcache_hits',0)
    r['dcache_misses']   = r.get('dcache_misses',0)

    r['icache_accesses'] = r.get('icache_accesses',0)
    r['icache_hits']     = r.get('icache_hits',0)
    r['icache_misses']   = r.get('icache_misses',0)

    for l in [2,3]:
        for q in ['accesses', 'hits', 'misses']:
            for p in ['demand', 'prefetch']:
                r[f'l{l}_{p}_{q}'] = r.get(f'l{l}_{p}_{q}',0)
        for q in ['accesses', 'hits', 'misses']:
            r[f'l{l}_total_{q}'] = r[f'l{l}_demand_{q}'] + r[f'l{l}_prefetch_{q}']
        for p in ['demand', 'prefetch', 'total']:
            r[f'l{l}_{p}_miss_rate']   = rate_or_zero(r[f'l{l}_{p}_misses'],r[f'l{l}_{p}_accesses'])


    r['dcache_miss_rate']  = rate_or_zero(r['dcache_misses'],r['dcache_accesses'])
    r['icache_miss_rate']  = rate_or_zero(r['icache_misses'],r['icache_accesses'])
    
    r['CI_Vector_ls'] = r.get('CI_Vector_loads',0) + r.get('CI_Vector_stores',0)
    r['CI_Scalar_ls'] = r.get('CI_Scalar_loads',0) + r.get('CI_Scalar_stores',0)

    return r  


def normalize(r: dict):
    r = normalize_clocks(r)
    r = normalize_ruby(r)
    r = normalize_cpu(r)
    r = normalize_memory(r)
    r = normalize_caches(r)

    return r
