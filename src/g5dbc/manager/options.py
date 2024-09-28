from dataclasses import dataclass
from pathlib import Path
import argparse
import os

@dataclass
class Options:
    benchmark_mod: Path|None
    path_prefix:   Path
    templates_dir: Path
    parser_re_dir: Path
    artifacts:     Path
    results_dir:   Path
    parser_out:    Path
    gem5_bin:      Path
    gem5_script:   Path
    benchmark_cfg: Path|None
    gem5_debug_opts:  str
    gem5_script_opts: str
    parser_format:    str
    generate: bool
    parse:    bool
    plots:    bool
    nprocs: int

    def __post_init__(self):
        self.path_prefix   = Path(self.path_prefix).resolve()
        self.artifacts     = Path(self.artifacts).resolve()
        self.results_dir   = Path(self.results_dir).resolve()
        self.templates_dir = Path(self.templates_dir).resolve()
        self.parser_re_dir = Path(self.parser_re_dir).resolve()
        self.parser_out    = Path(self.parser_out).resolve()
        self.gem5_bin      = Path(self.gem5_bin).resolve()
        self.gem5_script   = Path(self.gem5_script).resolve()

        if self.benchmark_mod is not None:
            benchmark_mod = Path(self.benchmark_mod) #.resolve()
            if len(benchmark_mod.parts) == 1:
                self.benchmark_mod = self.path_prefix.joinpath("share/g5dbc/benchmarks", benchmark_mod)
            else:
                self.benchmark_mod = benchmark_mod

        if self.benchmark_cfg is not None:
            benchmark_cfg = Path(self.benchmark_cfg) #.resolve()
            if len(benchmark_cfg.parts) == 1:
                self.benchmark_cfg = self.path_prefix.joinpath("share/g5dbc/configs", benchmark_cfg)
            else:
                self.benchmark_cfg = benchmark_cfg

    @classmethod
    def parse_from_args(cls):
        parser = argparse.ArgumentParser(description="Configuration")
        
        parser.add_argument(
            "--benchmark-mod", metavar="benchmark.py", type=str, help="Benchmark Python module")
        parser.add_argument(
            "--path-prefix",   type=str, default="/usr", help="Path Prefix")
        parser.add_argument(
            "--artifacts",     type=str, default=None, help="Artifacts Manifest")
        parser.add_argument(
            "--benchmark-cfg", type=str, default=None, help="Configuration File")
        parser.add_argument(
            "--results-dir",   type=str, default=None, help="Results Directory")
        parser.add_argument(
            "--parser-out",    type=str, default=None, help="Parsed Results Directory")
        parser.add_argument(
            "--templates-dir", type=str, default=None, help="Templates Directory")
        parser.add_argument(
            "--parser-re-dir", type=str, default=None, help="Parser regexps Directory")
        parser.add_argument(
            "--parser-format", type=str, default="flatjs", help="Parser format")
        parser.add_argument(
             "--gem5-bin",     type=str, default=None, help="gem5 binary")
        parser.add_argument(
             "--gem5-debug-opts",  type=str, default="", help="gem5 debug options")
        parser.add_argument(
             "--gem5-script-opts", type=str, default="", help="gem5 script options")
        parser.add_argument(
            "--generate", action='store_true', default=False, help="Generate workload")
        parser.add_argument(
            "--parse",    action='store_true', default=False, help="Parse results")
        parser.add_argument(
            "--plots",    action='store_true', default=False, help="Generate plots from results")
        parser.add_argument(
            "--nprocs",   type=int, default=1, help="Number of processes in pool")

        args = parser.parse_args()

        if args.artifacts is None:
             args.artifacts = f"{args.path_prefix}/share/g5dbc/artifacts.yaml"

        if args.templates_dir is None:
             args.templates_dir = f"{args.path_prefix}/share/g5dbc/templates"

        if args.parser_re_dir is None:
             args.parser_re_dir = f"{args.path_prefix}/share/g5dbc/parser"

        if args.gem5_bin is None:
             args.gem5_bin = f"{args.path_prefix}/bin/gem5.bin"
            
        if args.results_dir is None:
             args.results_dir = f"{os.getcwd()}/results"

        if args.parser_out is None:
             args.parser_out = f"{os.getcwd()}/parsed"

        gem5_script = str(Path(__file__).parent.joinpath("../../main.py").resolve())

        return cls(gem5_script=gem5_script,**vars(args))
