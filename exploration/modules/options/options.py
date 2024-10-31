import argparse
import os
import subprocess
import sys

from pathlib import Path


def select_path(user_path, pres_path, optional=False):
    """Helper function for selecting and verifying file path parameters"""
    # Check if user has provided a path. 
    if user_path:
        path = Path(user_path).resolve()
        if path.exists():
            return path
        else:
            sys.exit(f'User given path {user_path} does not exist')
    # Check if preselected path exists
    if pres_path:
        path = Path(pres_path).resolve()
        if path.exists():
            return path
        else:
            if optional:
                return None
            else:
                sys.exit(f'Required path {pres_path} does not exist')
    if optional:
        return None
    else:
        sys.exit(f'Required path not defined')

def select_root_partition(disk_path, user_part, pres_part="/dev/vda"):
    """Helper function for selecting correct root partition"""
    # If root partition already given by user, return
    if user_part:
        return user_part
    path = Path(disk_path).resolve()
    try:
        # Try using file command to gather information
        output = subprocess.run(['file', '-b', path], stdout=subprocess.PIPE).stdout.decode('utf-8')
    except FileNotFoundError:
        output = ""
    # If disk image contains a partition table,
    # assume root partition is first one
    part = f"{pres_part}1" if "partition" in output else pres_part
    return part
        

class Options:
    """Parse command line options"""
    def __init__(self):
        parser = argparse.ArgumentParser(description="Configuration")
        
        parser.add_argument("--generate", action='store_true', default=False, help="Generate workload")
        parser.add_argument("--parse",    action='store_true', default=False, help="Parse results")
        parser.add_argument('--use-multiprocessing', action='store_true', default=False, help='Use Multiprocessing backend for parsing ROIs')
        parser.add_argument("--plots",    action='store_true', default=False, help="Generate plots from results")
        parser.add_argument("--amd-template",  action='store_true', default=False, help="Generate template for AMD-CTE")

        parser.add_argument("--benchmark",    type=str, default=None,  help="Benchmark name")

        parser.add_argument("--se-mode",     action='store_true', default=False, help="System Emulation mode")
        parser.add_argument("--checkpoint",  action='store_true', default=False, help="Create checkpoint")
        parser.add_argument("--restore-checkpoint",  action='store_true', default=False, help="Restore from checkpoint")

        parser.add_argument("--gem5-bin",     type=str, default=None, help="gem5 binary")
        parser.add_argument("--gem5-script",  type=str, default=None, help="gem5 script")

        parser.add_argument("--results-dir",  type=str, default=None, help="Results directory")
        parser.add_argument("--objects-dir",  type=str, default=None, help="Objects directory containing gem5.bin, Linux kernel, bootloader and disk images")
        parser.add_argument("--config-dir",   type=str, default=None, help="Configuration directory")
        parser.add_argument("--binary-dir",   type=str, default=None, help="Binary directory")

        parser.add_argument("--config",       type=str, default=None, help="Configuration File")
        parser.add_argument("--config-files", type=str, default=None, nargs='*', help="Configuration Files")

        parser.add_argument("--kernel",     type=str, default=None, help="Linux kernel image")
        parser.add_argument("--bootloader", type=str, default=None, help="Bootloader")
        parser.add_argument("--bootscript", type=str, default=None, help="Boot script")
        parser.add_argument("--rootdisk",   type=str, default=None, help="Root Disk image")
        parser.add_argument("--benchdisk",  type=str, default=None, help="Data Disk image")
        parser.add_argument("--root-partition", type=str, default=None, help="Root partition")

        parser.add_argument("--gem5-debug-flags",  type=str, default=None, help="Gem5 Debug Flags")



        options = parser.parse_args()
        
        self.generate     = options.generate
        self.parse        = options.parse
        self.plots        = options.plots
        self.amd_template = options.amd_template

        self.use_multiprocessing = options.use_multiprocessing
        
        if (not (self.generate or self.parse or self.plots)):
            self.generate = True

        self.benchmark  = options.benchmark
        self.fs_mode    = not options.se_mode
        self.checkpoint = options.checkpoint
        self.restore_checkpoint = options.restore_checkpoint

        self.gem5_debug_flags = options.gem5_debug_flags

        base_dir  = Path(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..')))

        self.results_dir  = Path(options.results_dir) if options.results_dir else Path.cwd().joinpath(self.benchmark)
        self.objects_dir  = Path(options.objects_dir) if options.objects_dir else Path.cwd().joinpath('objects')
        self.binary_dir   = Path(options.binary_dir)  if options.binary_dir  else self.objects_dir.joinpath('bin')
        self.config_dir   = Path(options.config_dir)  if options.config_dir  else base_dir.joinpath('exploration', 'architectures')
        self.checkpoint_dir  = Path(os.getenv("RUNDIR")) if os.getenv("RUNDIR") else Path.cwd().joinpath('cpts')

        self.kernel      = select_path(options.kernel,      self.objects_dir.joinpath('binaries', 'vmlinux'))
        self.bootloader  = select_path(options.bootloader,  self.objects_dir.joinpath('binaries', 'boot_v2.arm64'))
        self.rootdisk    = select_path(options.rootdisk,    self.objects_dir.joinpath('disks', 'rootfs.img'))
        self.benchdisk   = select_path(options.benchdisk,   self.objects_dir.joinpath('disks', 'benchmarks.img'), optional=True)
        self.gem5_bin    = select_path(options.gem5_bin,    self.objects_dir.joinpath('gem5.bin'))
        self.gem5_script = select_path(options.gem5_script, base_dir.joinpath('gem5', 'simulate.py'))

        self.root_partition = select_root_partition(self.rootdisk, options.root_partition)

        if(options.config):
            self.config_files = [self.config_dir.joinpath(f"{options.config}.yaml")]
        else:
            self.config_files = list(map(lambda x: Path(x), options.config_files) if options.config_files else self.config_dir.glob('*.yaml'))
        
        self.config_names   = list(map(lambda x: x.stem,  self.config_files))
        self.configurations = dict(zip(self.config_names, self.config_files))
        
        self.ckpt_template = os.path.join(base_dir,'exploration','templates','cpt.sh')

        if options.bootscript:
            self.work_template = options.bootscript
        else:
            self.work_template = os.path.join(base_dir,'exploration','templates','work.sh')

        if self.fs_mode:
            self.srun_template = os.path.join(base_dir,'exploration','templates','srun_fs.sh')
        else:
            self.srun_template = os.path.join(base_dir,'exploration','templates','srun_se.sh')

