import itertools
import os
import re

from modules import Options

def iterate(m):
    k, v = zip(*m.items())
    l = list(dict(zip(k, p)) for p in itertools.product(*v))
    return l


class Benchmark:
    name = None

    keys = ['benchmark']
    sort = ['benchmark']
    group_by = ['casename']

    def __init__(self, options: Options, **kwargs):
        self.options = options

        self.binary_dir  = options.binary_dir
        self.fs_mode     = options.fs_mode
        self.conf        = options.config_names
        self.checkpoint  = options.checkpoint
        self.results_dir = options.results_dir
        self.roi_glob    = "*.roi.[0-9]*"
        self.parameters  = dict(
            conf=self.conf
            )
        self.reduce_cols = dict(
            CI_FLOPS_cycle = ['min','max','mean', 'std', 'count'],
            bw_gem5_GB = ['min','max','mean', 'std', 'count']
        )

        # Update the parameters instance variable with the benchmark parameters defined above
        p = self.get_parameters(options)
        self.parameters.update(p)


    def get_parameters(self, options):
        """
        Define benchmark parameters
        """

        return dict()

    def iterate_parameters(self, checkpoint=False):
        p = []
        if checkpoint:
            if self.checkpoint:
                p = iterate({
                    'cpus': self.parameters.get('cpus',[1]),
                    'conf' :self.conf
                    })
            else:
                p = []
        else:
            p = iterate(self.parameters)
        return p

    def check_parameters(self, parameters: dict, conf_dict: dict):
        return True

    def update_conf(self, parameters: dict, conf_dict: dict):

        if self.fs_mode:
            conf_dict['simulation']['fs_mode'] = True
        else:
            conf_dict['simulation']['fs_mode'] = False

        return conf_dict

    def get_checkpoint_name(self, parameters: dict):

        name = 'EPI-checkpoint-{}-{}'.format(self.name, 'sve_{sve_vl}-cpus_{cpus}-threads_{threads}'.format(**parameters))

        return name

    def get_name(self, parameters: dict, conf_dict: dict, checkpoint=False):
        #parameters = conf_dict['parameters']
        if checkpoint:
            name = '{conf}-{cpus}'.format(**parameters)
            return name
        else:
            name = 'EPI-{}-{}'.format(self.name, '-'.join(['{}_{}'.format(k,v) for k,v in parameters.items()]))
            return name

    def get_env_dict(self, parameters: dict, conf_dict: dict):
        env_dict = {}

        cpus = conf_dict['system']['num_cpus']

        # Execution environment should not move OpenMP threads
        env_dict['OMP_PROC_BIND'] = 'true'

        env_dict['GOMP_CPU_AFFINITY'] = f'0-{cpus-1}' if (cpus>1) else '0'

        # Set SVE_VEC_LEN variable, which is used to set the system SVE vector length
        sve_vl = conf_dict['cpu']['sve_vl']
        env_dict['SVE_VEC_LEN']=int(sve_vl/8)

        return env_dict

    def get_command(self, parameters: dict, conf_dict: dict):
        return ''

    def parse_roi(self, rdict: dict, conf_dict: dict):
        rdict['benchmark']  = self.name
        rdict['conf']       = conf_dict['parameters']['conf']
        rdict['terminal_log'] = conf_dict['terminal_log']
        rdict['output_log']   = conf_dict['output_log']

        return rdict

    def parse_output_log(self, output_log: str):
        cdict = dict(
            links = dict(),
            router = dict(),
            network = dict(
                links = list()
            )
        )

        for l in iter(output_log.splitlines()):
            p = r"R(\d+)\.L(\d+)\.R(\d+)"
            m = re.search(p, l)
            if m:
                src  = int(m.group(1))
                link = int(m.group(2))
                dst  = int(m.group(3))
                cdict["links"][link] = {}
                cdict["links"][link]["src"] = src
                cdict["links"][link]["dst"] = dst

            p = r"EXT.(\w+)\.(\d+)\.(\w+)\.L(\d+)\.R(\d+)"
            m = re.search(p, l)
            if m:
                node   = m.group(1)
                ctrlId = int(m.group(2))
                ctrl   = m.group(3)
                link   = int(m.group(4))
                router = int(m.group(5))

                cdict["router"][router] = {}
                cdict["router"][router]["node"] = node
                cdict["router"][router]["dst"] = int(dst)

            p = r"make(\w+)Link src=(\d+) (\w+)Id=(\d+) linkId=(\d+) dest=(\d+) (\w+)Id=(\d+)"
            m = re.search(p, l)
            if m:
                item = dict(
                    linkType = m.group(1),
                    src = int(m.group(2)),
                    srcType = m.group(3),
                    srcId = int(m.group(4)),
                    linkId = int(m.group(5)),
                    dest = int(m.group(6)),
                    destType = m.group(7),
                    destId = int(m.group(8)),
                )

                cdict["network"]["links"].append(item)
        return cdict

    def parse_terminal_log(self, terminal_log: str):
        rdict = dict()
        return rdict

    def write_plots(self):
        return


