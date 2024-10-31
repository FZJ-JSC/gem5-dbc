from pathlib import Path

from modules.stats import parsers



def read_config_parameters(roi_file: Path, conf_dict: dict):

    r = dict(
        casename = roi_file.stem,
        filename = roi_file.name,
        iter     = int(roi_file.suffix[1:]),
        sve_vl        = conf_dict['cpu']['sve_vl'],
        num_cpus      = conf_dict['system']['num_cpus'],
        num_mem_ctrls = sum([m['channels'] for m in conf_dict['memory']]),
        num_threads   = conf_dict['parameters'].get('threads', conf_dict['system']['num_cpus']),
        flit_size_bytes = 72,

        topology = conf_dict['parameters']['conf'],
    )

    return r

def parse_roi(roi_file: Path, conf_dict: dict):

    # Initialize ROI dict
    r = read_config_parameters(roi_file,conf_dict)

    # Update ROI dict with parsed values
    r.update(
        parsers.parse_file(roi_file, parsers.get_parsers(conf_dict))
    )
    # Normalize ROI values
    r = parsers.normalize(r)

    for k,v in conf_dict['parameters'].items():
        r[f'p_{k}'] = v

    return r
