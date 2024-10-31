import os
from modules import Benchmark

class Template:
    def __init__(self, benchmark: Benchmark, conf_dict: dict):
        
        parameters = conf_dict['parameters']

        self.modules     = '' #'module load GCC/10.3.0 Python zlib gperf protobuf'
        self.gem5_bin    = benchmark.options.gem5_bin
        self.gem5_script = benchmark.options.gem5_script
        self.gem5_args   = ''
        self.kernel      = benchmark.options.kernel
        self.bootloader  = benchmark.options.bootloader
        self.rootdisk    = benchmark.options.rootdisk
        self.rootpart    = benchmark.options.root_partition
        self.benchdisk   = ''
        #self.ruby        = '--ruby' if options.ruby else ''
        self.bootscript  = 'work.sh'
        self.srunscript  = 'srun.sh'
        self.cmd_output  = 'stdout.txt'
        self.cmd_outerr  = 'stderr.txt'
        self.cmd_env     = 'environment.txt'

        self.checkpoint = ''

        self.name = benchmark.get_name(parameters, conf_dict)
        self.outd = os.path.join(benchmark.options.results_dir, self.name)
        self.conf = os.path.join(self.outd, '{}.yaml'.format(self.name))

        self.benchmark_cmd = benchmark.get_command(parameters, conf_dict)
        self.env_vars      = '\n'.join(
                ['export {}="{}"'.format(k,v) for k,v in benchmark.get_env_dict(parameters, conf_dict).items()]
            ) + '\n'

        self.debug_opts = ""
        if benchmark.options.amd_template: 
            self.amd_preamble = "\n".join([
                "module load anaconda", 
                "source activate gem5", 
                "export LD_LIBRARY_PATH=/apps/ANACONDA/2022.05/envs/gem5/lib"
            ])
        else: 
            self.amd_preamble = ""

        if benchmark.options.gem5_debug_flags:
            self.debug_opts = "--debug-flags={}".format(benchmark.options.gem5_debug_flags)

    def as_dict(self):
        return self.__dict__
