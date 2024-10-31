from pathlib import Path

import numpy as np

from modules.graphics import write_violinplot
from modules.stats.readers import read_rows
from modules.stats.table import concatenate_columns
from modules.stats.table import aggregate_list

default_violin_plots = [
    dict(
        suffix = "cycles",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'cycles',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "CPU_issueRate",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_issueRate',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "CPU_fuBusy",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_fuBusy',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "CPU_fuBusyRate",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_fuBusyRate',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "CPU_totalIpc",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_totalIpc',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix = "CPU_vecInstQueueReads",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_vecInstQueueReads',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix = "CPU_blockCycles",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_blockCycles',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix = "CPU_DECODE_blockedCycles",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_DECODE_blockedCycles',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix = "CPU_statFuBusy_MemRead",
        desc = 'Time-to-solution in Cycles',
        y_label = 'TTS [cycles]',
        value_col = 'CPU_statFuBusy_MemRead',
        bar_label = "{:.2f}",
    ),

    dict(
        suffix = "instructions_per_cycle",
        desc = 'Instructions/cycle',
        y_label = 'Instructions/cycle',
        value_col = 'CommittedInsts_cycle',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix = "flops_per_cycle",
        desc = 'FLOPS/cycle',
        y_label = 'FLOPS/cycle',
        value_col = 'CI_FLOPS_cycle',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix = "mem_bus_rw_utilization",
        desc = 'Memory Bus Utilization',
        y_label = r'Memory Bus Utilization [\%]',
        value_col = 'mem_bus_rw_util',
        bar_label = "{:.2%}",
        scale = "percentage"
    ),
    dict(
        suffix = "mem_ctrls_bytes_written",
        desc = 'Data written by memory controller',
        y_label = 'Memory Writes [bytes]',
        value_col = 'mem_ctrls_bytes_written',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "mem_ctrls_bytes_read",
        desc = 'Data read by memory controller',
        y_label = 'Memory Reads [bytes]',
        value_col = 'mem_ctrls_bytes_read',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "mem_ctrls_bytes_rw",
        desc = 'Data read+written by memory controller',
        y_label = 'Memory Reads+Writes [bytes]',
        value_col = 'mem_ctrls_bytes_rw',
        bar_label = "{:.2E}",
    ),
    dict(
        suffix = "FLOPS_Bytes",
        desc = 'Computational Intensity [Flops/Bytes]',
        y_label = 'Computational Intensity [Flops/Bytes]',
        value_col = 'FLOPS_Bytes',
        bar_label = "{:.2f} Flops/Bytes",
    ),
    dict(
        suffix = "Bytes_FLOPS",
        desc = 'Code Balance [Bytes/Flops]',
        y_label = 'Code Balance [Bytes/Flops]',
        value_col = 'Bytes_FLOPS',
        bar_label = "{:.2f} Bytes/Flops",
    ),
    dict(
        suffix = "bw_gem5_GB",
        desc = 'Memory Bandwidth at controller [GB/s]',
        y_label = 'Memory Bandwidth at controller [GB/s]',
        value_col = 'bw_gem5_GB',
        bar_label = "{:.2f} GB/s",
    ),
    dict(
        suffix = "bw_reported",
        desc = 'Reported Bandwidth [GB/s]',
        y_label = 'Reported Bandwidth [GB/s]',
        value_col = 'bw_reported',
        bar_label = "{:.2f} GB/s",
    ),
    dict(
        suffix = "bw_bytes_cycle",
        desc = 'Memory Bandwidth at controller bytes/cycle]',
        y_label = 'Memory Bandwidth at controller [bytes/cycle]',
        value_col = 'bw_bytes_cycle',
        bar_label = "{:.2f} bytes/cycle",
    ),
    dict(
        suffix = "CI_FLOPS_cycle",
        desc = 'FLOPS/Cycle',
        y_label = 'FLOPS/Cycle',
        value_col = 'CI_FLOPS_cycle',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_network",
        value_col = 'mesh_avg_flit_latency_network',
        y_label   = 'Average Flit Network Latency [cycles]',
        desc      = 'Average Flit Network Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_queueing",
        value_col = 'mesh_avg_flit_latency_queueing',
        y_label   = 'Average Flit Queueing Latency [cycles]',
        desc      = 'Average Flit Queueing Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    dict(
        suffix    = "mesh_avg_flit_latency_total",
        value_col = 'mesh_avg_flit_latency_total',
        y_label   = 'Average Flit Total Latency [cycles]',
        desc      = 'Average Flit Total Latency [cycles]',
        bar_label = "{:.2f}",
    ),
    # dict(
    #     suffix = "l3_total_accesses",
    #     desc = 'SLC Total Accesses',
    #     y_label = 'SLC Total Accesses',
    #     value_col = 'l3_total_accesses',
    #     bar_label = "{:.2E}",
    # ),
    # dict(
    #     suffix = "l3_total_hits",
    #     desc = 'SLC Total Hits',
    #     y_label = 'SLC Total Hits',
    #     value_col = 'l3_total_hits',
    #     bar_label = "{:.2E}",
    # ),
    # dict(
    #     suffix = "l3_total_misses",
    #     desc = 'SLC Total Misses',
    #     y_label = 'SLC Total Misses',
    #     value_col = 'l3_total_misses',
    #     bar_label = "{:.2E}",
    # ),
    # dict(
    #     suffix = "time",
    #     desc = 'Time-to-solution in Seconds',
    #     y_label = 'TTS [s]',
    #     value_col = 'time',
    #     bar_label = "{:.2E}",
    #),
]

def write_violin_plots(data_dir: Path, plot_dir: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_dir, select_rows, fmtstr = "{benchmark}_cols.txt")

    if len(rows.index) > 0:
        for p in [*default_violin_plots, *extra_plots]:
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

            stats, agg_col = aggregate_list(rows, v_col, [i_col, o_col])

            #print(f"{stats}")
            #print(f"{x_vals}")
            #print(f"{labels}")

            #xy_data = {s:dict(vals=stats[stats[i_col]==s].set_index(o_col).to_dict()) for s in labels}
            xy_data = {s:dict(vals=stats[stats[i_col]==s][[o_col,v_col]].set_index(o_col).to_dict()[v_col]) for s in labels}

            #print(f"{xy_data}")

            xy_values = dict()
            for k, v in xy_data.items():
                xy_values[k] = dict(
                    x_labels = x_vals,
                    x = np.arange(len(x_vals)),
                    y = [v['vals'].get(x,0) for x in x_vals]
                )
            
            #print(f"{xy_values}")
            #    for s in ['mean', 'std']:
            #        xy_values[k][s] = [v['vals'][s].get(x,0) for x in x_vals]


            filename = plot_dir.joinpath(plot_params['fname_fmt'].format(**params))

            print(f"Writing image to {filename}")
            #print(f"{xy_values}")

            write_violinplot(filename, xy_values, params)
