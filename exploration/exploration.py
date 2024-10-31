#!/usr/bin/env python3

import importlib
import os
import yaml
from pathlib import Path
from typing import List
from time import time
from copy import deepcopy 

import multiprocessing

from modules import Options
from modules import Benchmark
from modules import Template

from modules.stats import parse_roi
from modules.stats.writers import write_data_simulators

try: 
    from tqdm import tqdm
    has_tqdm = True
except ImportError:
    has_tqdm = False


def generate_workload(benchmark: Benchmark, options: Options):

    for p in benchmark.iterate_parameters():

        conf_path = benchmark.options.configurations[p['conf']]
        conf_dict = yaml.safe_load(Path(conf_path).read_text())
        # Store parameters
        conf_dict['parameters'] = {**p}

        if not benchmark.check_parameters(p,conf_dict):
            continue

        conf_dict = benchmark.update_conf(p,conf_dict)

        template  = Template(benchmark, conf_dict)

        # Set secondary benchdisk if present
        if(options.benchdisk):
            template.benchdisk = '--disk {}'.format(options.benchdisk)

        # Three ways to run simulations
        # 1. --checkpoint-mode: Create checkpoint within simulated application (ROI) - runs in atomic to completion
        # 2. --checkpoint-restore: Restore from checkpoint in detailed mode
        # 3. default: boots kernel in atomic and switch cpu after boot (via first m5exit of bootscript)

        # Create Checkpoints
        if(options.checkpoint):
            cpt_dir = os.path.join(options.checkpoint_dir, 'cpts', benchmark.get_checkpoint_name(p))
            template.checkpoint = '--checkpoint-mode --checkpoint-directory {}'.format(cpt_dir)
            os.makedirs(cpt_dir, exist_ok=True)

        # Restore from checkpoint
        if(options.restore_checkpoint):
            cpt_dir = os.path.join(options.checkpoint_dir, 'cpts', benchmark.get_checkpoint_name(p))
            template.checkpoint = '--checkpoint-restore 1 --checkpoint-directory {}'.format(cpt_dir)

        # Create output directory
        os.makedirs(template.outd, exist_ok=True)

        # Write config params to local config file
        Path(template.conf).write_text(yaml.dump(conf_dict, default_flow_style=False))

        # Write srun script
        srun_file = os.path.join(template.outd, template.srunscript)
        Path(srun_file).write_text(Path(benchmark.options.srun_template).read_text().format(**template.as_dict()))
        os.chmod(srun_file, 0o744)

        if benchmark.options.fs_mode:
            # Write work script
            work_file = os.path.join(template.outd, template.bootscript)
            Path(work_file).write_text(Path(benchmark.options.work_template).read_text().format(**template.as_dict()))
        else:
            # Write env variables
            work_file = os.path.join(template.outd, template.cmd_env)
            Path(work_file).write_text(template.env_vars)

    return 0


def parse_workload_single_core(benchmark: Benchmark, subdirs: List[Path], cpu_id): 
    dicts = []

    nsubdir = len(subdirs)
    if has_tqdm: 
        subdirs_iterator = tqdm(subdirs, desc=f"[CPU {cpu_id}]", position=cpu_id)
    else: 
        subdirs_iterator = subdirs


    for idx, results_dir in enumerate(subdirs_iterator):
        name = results_dir.name

        if not has_tqdm: print(f"Parsing subdir {name} {idx}/{nsubdir}")

        config_file = results_dir.joinpath(f"{name}.yaml")
        output_file = results_dir.joinpath(f"output.log")
        terminal_file = results_dir.joinpath(f"system.terminal")

        if output_file.is_file():
            # Read conf_dict
            conf_dict = yaml.safe_load(config_file.read_text())

            # Parse output file
            conf_dict['output_log'] = benchmark.parse_output_log(output_file.read_text())
            # Parse terminal output
            conf_dict['terminal_log'] = benchmark.parse_terminal_log(terminal_file.read_text())

            for roi_file in results_dir.glob(benchmark.roi_glob):
                if not has_tqdm: print(f"   - {roi_file}")
                r = parse_roi(roi_file, conf_dict)
                r = benchmark.parse_roi(r,conf_dict)
                dicts.append(r)
    return dicts

def make_chunks(benchmark, subdirs):
    cpu_count = 108
    chunks = []
    elems_per_chunk = len(subdirs) // cpu_count

    # Silence warning "i is possibly unbound"
    i = 0

    for i in range(cpu_count - 1):
        chunks.append((deepcopy(benchmark), deepcopy(subdirs[i * elems_per_chunk: (i + 1) * elems_per_chunk]), i))

    chunks.append((deepcopy(benchmark), deepcopy(subdirs[(i+1) * elems_per_chunk:]), i))
    assert(len(subdirs) == sum([len(chunk) for _, chunk, _ in chunks]))
    return chunks


def parse_workload(benchmark: Benchmark, options: Options):

    os.system("clear")
    begin_parsing = time() 
    dicts = []

    subdirs = [d for d in Path(benchmark.results_dir).iterdir() if d.is_dir()]

    if options.use_multiprocessing: 
        chunks = make_chunks(benchmark, subdirs)
        if has_tqdm: 
            with multiprocessing.Pool(108, initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),)) as pool:
                results = pool.starmap(parse_workload_single_core, chunks)
                for r in results: 
                    dicts.extend(r)
        else: 
            with multiprocessing.Pool(108) as pool:
                results = pool.starmap(parse_workload_single_core, chunks)
                for r in results: 
                    dicts.extend(r)
    else: 
        dicts = parse_workload_single_core(benchmark, subdirs, 0)

    end_parsing = time()

    os.system("clear")
    print(f"Parsing took: {(end_parsing - begin_parsing):.2f}s")
    
    write_data_simulators(benchmark, dicts, options.results_dir, select_rows = dict(iter=1))

    return 0

def generate_plots(benchmark: Benchmark, options: Options):
    benchmark.write_plots()
    return 0


def main():
    options = Options()
    app = importlib.import_module('benchmarks.{}'.format(options.benchmark))
    benchmark : Benchmark = app.Benchmark(options)

    if options.generate:
        print(f"Generating scripts for {benchmark.name}")
        generate_workload(benchmark, options)
    if options.parse:
        print(f"Parsing workload for {benchmark.name}")
        parse_workload(benchmark, options)
    if options.plots:
        print(f"Generating plots for {benchmark.name}")
        generate_plots(benchmark, options)

    return 0


if __name__ == "__main__":
    main()
