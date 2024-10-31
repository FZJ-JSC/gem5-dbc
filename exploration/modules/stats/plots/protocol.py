import math
import re
from pathlib import Path

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot


default_plots = [
        dict(
            suffix = "{cache}_{event}_{init}_{end}",
            cache = 'l1d',
            event = 'Load',
            init  = 'I',
            end   = 'SC',
            col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
            max_x   = 1500,
            x_label = 'Cycles',
            y_label = 'Events',
        ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Load',
    #         init  = 'SC',
    #         end   = 'SC',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Load',
    #         init  = 'UD',
    #         end   = 'UD',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),

    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Store',
    #         init  = 'I',
    #         end   = 'I',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Store',
    #         init  = 'I',
    #         end   = 'UD',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Store',
    #         init  = 'UD',
    #         end   = 'UD',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),

    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Local_Eviction',
    #         init  = 'UD',
    #         end   = 'I',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l1d',
    #         event = 'Local_Eviction',
    #         init  = 'SC',
    #         end   = 'I',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
        
    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l1d',
    #         event = 'SendReadShared',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l1d',
    #         event = 'SendReadUnique',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x   = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l1d',
    #         event = 'SendWriteBackOrWriteEvict',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l1d',
    #         event = 'SendEvict',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),

    # #L2
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l2',
    #         event = 'ReadShared',
    #         init  = 'I',
    #         end   = 'UC_RSC',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l2',
    #         event = 'ReadUnique',
    #         init  = 'I',
    #         end   = 'UC_RU',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l2',
    #         event = 'Evict',
    #         init  = 'UC_RSC',
    #         end   = 'UC',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l2',
    #         event = 'WriteBackFull',
    #         init  = 'UC_RU',
    #         end   = 'UD',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l2',
    #         event = 'Local_Eviction',
    #         init  = 'UC',
    #         end   = 'I',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 100,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'l2',
    #         event = 'Local_Eviction',
    #         init  = 'UD',
    #         end   = 'I',
    #         col_regex = r"caches_{cache}_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 100,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),

    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l2',
    #         event = 'SendReadShared',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l2',
    #         event = 'SendReadUnique',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'l2',
    #         event = 'SendWriteBackOrWriteEvict',
    #         col_regex = r"caches_{cache}_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x = 100,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),


    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'I',
    #         end   = 'RU',
    #         event = 'ReadShared',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 600,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'I',
    #         end   = 'RU',
    #         event = 'ReadUnique_PoC',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 300,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'UD',
    #         end   = 'RU',
    #         event = 'ReadUnique_PoC',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 200,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),

    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'RU',
    #         end   = 'UD',
    #         event = 'WriteBackFull',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 100,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'RU',
    #         end   = 'UC',
    #         event = 'WriteEvictFull',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 100,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),


    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'I',
    #         end   = 'UD',
    #         event = 'WriteUniqueFull_PoC_Alloc',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 100,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'UC',
    #         end   = 'I',
    #         event = 'LocalHN_Eviction',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 1500,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    #     dict(
    #         suffix = "{cache}_{event}_{init}_{end}",
    #         cache = 'SLC',
    #         init = 'UD',
    #         end   = 'I',
    #         event = 'LocalHN_Eviction',
    #         col_regex = r"HNF_CHI_inTransLatSpHist_{event}_{init}_{end}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),

    #     dict(
    #         suffix = "{cache}_{event}",
    #         cache = 'SLC',
    #         event = 'SendWriteNoSnp',
    #         col_regex = r"HNF_CHI_outTransLatSpHist_{event}_b(\d+)",
    #         max_x = 50,
    #         x_label = 'Cycles',
    #         y_label = 'Events',
    #     ),
    ]


def write_protocol_latency_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if(len(rows.index) > 0):
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}
            
            i_col = params['inner_col']

            col_regex = params['col_regex'].format(**p)
            suffix = params['suffix'].format(**p)
            # Set max_x
            params['max_x'] = params.get(f"max_{suffix}", params['max_x'])
            min_x = params.get(f"min_{suffix}",params.get("min_x",0))

            sparse_cols = [c for c in rows if re.match(col_regex, c)]
            if not sparse_cols:
                continue

            # Read sparse data
            data = rows[sparse_cols+[i_col]].set_index(i_col).transpose().to_dict()

            xy_values = dict()
            for label, values in data.items():
                events = {int(next(iter( re.findall(col_regex, col) or []), 0)):v for col, v in values.items() if math.isfinite(v)}
                # Length x
                keys = events.keys()
                if keys:
                    len_x = max(keys) + 1
                    # produce coordinates for scatter plot
                    xy_values[label] = dict(
                        x = [i for i in range(min_x,len_x)],
                        y = [events.get(i,0) for i in range(min_x,len_x)]
                    )

            filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))

            #print(f"Writing image to {filename}")
            #for l,v in xy_values.items():
                #print(l,v["x"][0:11], v["y"][0:11])
            write_scatterplot(filename, xy_values, params)
