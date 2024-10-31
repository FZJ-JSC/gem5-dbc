# -*- coding: utf-8 -*-

from pandas import DataFrame
from pathlib import Path
import re
from time import time

from modules import Benchmark


default_cols = [
    # 'num_cpus', 'num_mem_ctrls',
    'cycles', 'time',
    #'CI_FLOPS_cycle',
    # 'flops_cycle_pc', 'FLOPS_Bytes', 'Bytes_FLOPS',
    #'CPU_CommittedInsts_cycle',
    #'FU_Int_cycle', 'FU_Float_cycle', 'FU_Simd_cycle', 'FU_FloatSimd_cycle', 'FU_Mem_cycle',
    #'CPU_numInsts','COMMIT_instsCommitted','COMMIT_opsCommitted',
    #'CI_Mem_Read', 'CI_Mem_Write',
    #'CI_FP_Simd','CI_FP_Float','CI_Int',
    #'COMMIT_vector_loads', 'COMMIT_vector_stores',
    #'COMMIT_scalar_loads', 'COMMIT_scalar_stores',
    # 'dcache_accesses', 'dcache_misses', 'dcache_miss_rate',
    # 'icache_accesses', 'icache_misses', 'icache_miss_rate',
    # 'l2_total_accesses',    'l2_total_misses',    'l2_total_miss_rate',
    # 'l3_total_accesses',    'l3_total_misses',    'l3_total_miss_rate',
    # 'l2_demand_accesses',   'l2_demand_misses',   'l2_demand_miss_rate',
    # 'l3_demand_accesses',   'l3_demand_misses',   'l3_demand_miss_rate',
    # 'l2_prefetch_accesses', 'l2_prefetch_misses', 'l2_prefetch_miss_rate',
    # 'l3_prefetch_accesses', 'l3_prefetch_misses', 'l3_prefetch_miss_rate',
    # # 'bw_gem5_GB', 'mem_peakBW', 'bw_bytes_cycle',
    # 'mem_bus_rw_util', 'mem_bus_read_util', 'mem_bus_write_util',
    # 'mem_ctrls_bytes_read', 'mem_ctrls_bytes_written', 'mem_ctrls_bytes_rw',
    # "mesh_total_hops", "mesh_total_hops_cycle", "mesh_average_hops",
    # "mesh_flits_received_total", "mesh_flits_received_cycle",
    # "mesh_avg_flit_latency_network",
    # "mesh_avg_flit_latency_queueing",
    # "mesh_avg_flit_latency_total",
    # "mem_ctrls_sum_avgMemAccLat",
    "mem_ctrls_sum_totalDispatchedLatency",
    "mem_ctrls_sum_latencyDispatchedCount",
    "mem_ctrls_sum_totalRequestedBandwidth",
    "mem_ctrls_sum_bandwidthRequestedCount",
    "mem_ctrls_sum_numReads",
    "mem_ctrls_sum_numWrites",
]

default_regex = [
    # r"CPU_", r"CI_", r"FU_",
    # r"cpu([0-9]*)_(l1d|l1i|l2)_demand_(accesses|hits|misses)$",
    # r"HNF([0-9]*)_demand_(accesses|hits|misses)$",
    # r"mem_ctrl(\d+)_bytesRead",
    # r"CI_FP_cpu([0-9]*)$", r"CI_FLOPS_cpu([0-9]*)$",
    # r"mesh_router_hops_hist_vnet(\d+)",
    # r"mesh_avg_flit_latency_network_vnet(\d+)",
    # r"mesh_avg_flit_latency_queueing_vnet(\d+)",
    # r"mesh_avg_flit_latency_total_vnet(\d+)",
    # r"mesh_flits_received_vnet(\d+)",
    # r"network_routers_vnet(\d+)_src_dst_total_packets_(all|ext|int)"
    # r"mem_ctrl(\d+)_avgMemAccLat",
    r"system\.mem_ctrl(\d+)_totalDispatchedLatency$",
    r"system\.mem_ctrl(\d+)_latencyDispatchedCount$",
    r"system\.mem_ctrl(\d+)_totalRequestedBandwidth$",
    r"system\.mem_ctrl(\d+)_bandwidthRequestedCount$",
    #r"cpu([0-9]*)_(l1d|l1i|l2)_(In|Out)_avg_(buf_msgs|stall_time)$",
    #r"cpu(\d*)_pf(\w+)_(\w+)$"
]

def write_data_simulators(benchmark: Benchmark, dicts: list, output_dir: Path,  select_rows = dict()):
    begin_df_creation = time()
    data = DataFrame(dicts)
    end_df_creation = time()
    print(f"Dataset creation took {(end_df_creation - begin_df_creation):.2f}s")
    keys = benchmark.keys
    keys.extend(default_cols)
    for r in default_regex:
        print(f"Adding cols matching {r}")
        keys.extend([c for c in data if re.match(r, c)])
    # Include ROI filename
    keys.extend(['filename'])
    # for k in benchmark.group_by:
    #     if not k in keys:
    #         keys.append(k)
    
    # Write small selection of rows
    path = str(output_dir.joinpath(f"{benchmark.name}_cols.txt"))
    print(f"Writing to {path}")
    cols = data[(data['kernel']!='None')][keys]
    cols.to_csv(path, index=False)

    # Write only selected rows
    path = str(output_dir.joinpath(f"{benchmark.name}_data_selected.h5"))
    print(f"Writing to {path}")
    slct = (data['kernel']!='None')
    for key,val in select_rows.items():
        slct=slct&(data[key]==val)
    cols = data[slct]
    cols.to_hdf(path, "data", format='fixed')

    # Write all data
    path = str(output_dir.joinpath(f"{benchmark.name}_data_all.h5"))
    print(f"Writing to {path}")
    data.to_hdf(path, "data", format='fixed')

    return data
