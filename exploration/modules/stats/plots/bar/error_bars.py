
from pathlib import Path

import numpy as np

from modules.graphics import plot_errorbarplot
from modules.stats.readers import read_rows
from modules.stats.table import concatenate_columns
from modules.stats.table import aggregate_statistics

cache_plots = [
    dict(
        suffix = "dcache_accesses",
        desc = 'Number of Data Cache Accesses',
        x_label = 'Number of Data Cache Accesses',
        value_col = 'dcache_accesses',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "dcache_hits",
        desc = 'Number of Data Cache Hits',
        x_label = 'Number of Data Cache Hits',
        value_col = 'dcache_hits',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "dcache_misses",
        desc = 'Number of Data Cache Misses',
        x_label = 'Number of Data Cache Misses',
        value_col = 'dcache_misses',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "l2_total_accesses",
        desc = 'L2 Cache Total Accesses',
        x_label = 'L2 Cache Total Accesses',
        value_col = 'l2_total_accesses',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "l2_total_hits",
        desc = 'L2 Cache Total Hits',
        x_label = 'L2 Cache Total Hits',
        value_col = 'l2_total_hits',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "l2_total_misses",
        desc = 'L2 Cache Total Misses',
        x_label = 'L2 Cache Total Misses',
        value_col = 'l2_total_misses',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "l3_total_accesses",
        desc = 'SLC Total Accesses',
        x_label = 'SLC Total Accesses',
        value_col = 'l3_total_accesses',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "l3_total_hits",
        desc = 'SLC Total Hits',
        x_label = 'SLC Total Hits',
        value_col = 'l3_total_hits',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "l3_total_misses",
        desc = 'SLC Total Misses',
        x_label = 'SLC Total Misses',
        value_col = 'l3_total_misses',
        bar_label = "{:.2E}",
    ),
]

time_plots = [
    dict(
        suffix = "cycles",
        desc = 'Time-to-solution in Cycles',
        x_label = 'TTS [cycles]',
        value_col = 'cycles',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "time",
        desc = 'Time-to-solution in Seconds',
        x_label = 'TTS [s]',
        value_col = 'time',
        bar_label = "{:.2E}",
    ),
]
network_plots = [
    dict(
        suffix    = "mesh_avg_flit_latency_network",
        value_col = 'mesh_avg_flit_latency_network',
        x_label   = 'Average Flit Network Latency [cycles]',
        desc      = 'Average Flit Network Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_queueing",
        value_col = 'mesh_avg_flit_latency_queueing',
        x_label   = 'Average Flit Queueing Latency [cycles]',
        desc      = 'Average Flit Queueing Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_total",
        value_col = 'mesh_avg_flit_latency_total',
        x_label   = 'Average Flit Total Latency [cycles]',
        desc      = 'Average Flit Total Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_network_vnet0",
        value_col = 'mesh_avg_flit_latency_network_vnet0',
        x_label   = 'VNET=0 Average Flit Network Latency [cycles]',
        desc      = 'VNET=0 Average Flit Network Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_network_vnet1",
        value_col = 'mesh_avg_flit_latency_network_vnet1',
        x_label   = 'VNET=1 Average Flit Network Latency [cycles]',
        desc      = 'VNET=1 Average Flit Network Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_network_vnet2",
        value_col = 'mesh_avg_flit_latency_network_vnet2',
        x_label   = 'VNET=2 Average Flit Network Latency [cycles]',
        desc      = 'VNET=2 Average Flit Network Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_network_vnet3",
        value_col = 'mesh_avg_flit_latency_network_vnet3',
        x_label   = 'VNET=3 Average Flit Network Latency [cycles]',
        desc      = 'VNET=3 Average Flit Network Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_queueing_vnet0",
        value_col = 'mesh_avg_flit_latency_queueing_vnet0',
        x_label   = 'VNET=0 Average Flit Queueing Latency [cycles]',
        desc      = 'VNET=0 Average Flit Queueing Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_queueing_vnet1",
        value_col = 'mesh_avg_flit_latency_queueing_vnet1',
        x_label   = 'VNET=1 Average Flit Queueing Latency [cycles]',
        desc      = 'VNET=1 Average Flit Queueing Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_queueing_vnet2",
        value_col = 'mesh_avg_flit_latency_queueing_vnet2',
        x_label   = 'VNET=2 Average Flit Queueing Latency [cycles]',
        desc      = 'VNET=2 Average Flit Queueing Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_queueing_vnet3",
        value_col = 'mesh_avg_flit_latency_queueing_vnet3',
        x_label   = 'VNET=3 Average Flit Queueing Latency [cycles]',
        desc      = 'VNET=3 Average Flit Queueing Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_total_vnet0",
        value_col = 'mesh_avg_flit_latency_total_vnet0',
        x_label   = 'VNET=0 Average Flit Total Latency [cycles]',
        desc      = 'VNET=0 Average Flit Total Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_total_vnet1",
        value_col = 'mesh_avg_flit_latency_total_vnet1',
        x_label   = 'VNET=1 Average Flit Total Latency [cycles]',
        desc      = 'VNET=1 Average Flit Total Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_total_vnet2",
        value_col = 'mesh_avg_flit_latency_total_vnet2',
        x_label   = 'VNET=2 Average Flit Total Latency [cycles]',
        desc      = 'VNET=2 Average Flit Total Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_total_vnet3",
        value_col = 'mesh_avg_flit_latency_total_vnet3',
        x_label   = 'VNET=3 Average Flit Total Latency [cycles]',
        desc      = 'VNET=3 Average Flit Total Latency [cycles]',
        bar_label = "{:.2f}",
    ),
]

memory_plots = [
    dict(
        suffix = "mem_bus_rw_utilization",
        desc = 'Memory Bus Utilization',
        x_label = r'Memory Bus Utilization [\%]',
        value_col = 'mem_bus_rw_util',
        bar_label = "{:.2%}",
        scale = "percentage"
    ),
    dict(
        suffix = "mem_ctrls_bytes_written",
        desc = 'Data written by memory controller',
        x_label = 'Memory Writes [bytes]',
        value_col = 'mem_ctrls_bytes_written',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "mem_ctrls_bytes_read",
        desc = 'Data read by memory controller',
        x_label = 'Memory Reads [bytes]',
        value_col = 'mem_ctrls_bytes_read',
        bar_label = "{:.2E}",
    ),
]

default_error_plots = [
    *time_plots,
    *memory_plots,
    *cache_plots,
    *network_plots,
]


def write_error_bar_plots(data_dir: Path, plot_dir: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_dir, select_rows, fmt = "csv")
    fname_fmt  = plot_params['fname_fmt']

    if len(rows.index) > 0:
        for p in [*default_error_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            rows, i_col = concatenate_columns(rows, params['inner_col'])
            rows, o_col = concatenate_columns(rows, params['outer_col'])
            rows, v_col = concatenate_columns(rows, params['value_col'])

            x_vals = sorted(rows[o_col].unique())
            labels = sorted(rows[i_col].unique())

            # Skip if data does not contain column
            if not v_col in rows.columns:
                print(f"Warning: {v_col} not found")
                continue

            stats, agg_col = aggregate_statistics(rows, v_col, [i_col, o_col])

            xy_data = {s:dict(vals=stats[stats[i_col]==s].set_index(o_col).to_dict()) for s in labels}

            xy_values = dict()
            for k, v in xy_data.items():
                xy_values[k] = dict(
                    x_labels = x_vals,
                    x = np.arange(len(x_vals)),
                )
                for s in ['mean', 'std']:
                    xy_values[k][s] = [v['vals'][s].get(x,0) for x in x_vals]


            filename = plot_dir.joinpath(fname_fmt.format(**params))

            print(f"Writing image to {filename}")
            #print(f"{xy_values}")

            #plot_errorbarplot(filename, xy_values, params)






