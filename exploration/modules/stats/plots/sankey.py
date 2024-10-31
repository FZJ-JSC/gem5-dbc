from pathlib import Path

from modules.graphics import write_sankey
from modules.stats import read_rows


default_plots = [
    dict(
        suffix = "network_routers_vnet0_src_dst",
        desc = 'VNET=Request Packets={:.2E}',
        value_col = 'network_routers_vnet0_src_dst',
        self_dest = True,
    ),
    dict(
        suffix = "network_routers_vnet1_src_dst",
        desc = 'VNET=Snoop Packets={:.2E}',
        value_col = 'network_routers_vnet1_src_dst',
        self_dest = True,
    ),
    dict(
        suffix = "network_routers_vnet2_src_dst",
        desc = 'VNET=Response Packets={:.2E}',
        value_col = 'network_routers_vnet2_src_dst',
        self_dest = True,
    ),
    dict(
        suffix = "network_routers_vnet3_src_dst",
        desc = 'VNET=Data Packets={:.2E}',
        value_col = 'network_routers_vnet3_src_dst',
        self_dest = True,
    ),

    dict(
        suffix = "network_routers_vnet0_src_dst_ex",
        desc = 'VNET=Request Packets={:.2E}',
        value_col = 'network_routers_vnet0_src_dst',
        self_dest = False,
    ),
    dict(
        suffix = "network_routers_vnet1_src_dst_ex",
        desc = 'VNET=Snoop Packets={:.2E}',
        value_col = 'network_routers_vnet1_src_dst',
        self_dest = False,
    ),
    dict(
        suffix = "network_routers_vnet2_src_dst_ex",
        desc = 'VNET=Response Packets={:.2E}',
        value_col = 'network_routers_vnet2_src_dst',
        self_dest = False,
    ),
    dict(
        suffix = "network_routers_vnet3_src_dst_ex",
        desc = 'VNET=Data Packets={:.2E}',
        value_col = 'network_routers_vnet3_src_dst',
        self_dest = False,
    ),
 ]    


def write_sankey_plots(directory: Path, benchmark_params: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(benchmark_params, directory)
    outer_cols = rows[plot_params['outer_col']].unique()
    inner_cols = rows[plot_params['inner_col']].unique()
    filefmt    = plot_params['sankey']['pathname']
    titlefmt   = plot_params['sankey']['titlefmt']
    for u in outer_cols:
        for v in inner_cols:
            params = {**benchmark_params}
            params[plot_params['outer_col']] = u
            params[plot_params['inner_col']] = v
            inner_rows = read_rows(params, directory)
            if(len(inner_rows.index) > 0):
                for p in [*default_plots, *extra_plots]:
                    all_params = dict(**p, **params, **plot_params, filefmt=filefmt)
                    write_sankey(inner_rows,all_params,directory)
