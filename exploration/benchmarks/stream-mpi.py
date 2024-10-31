import modules

from modules import Options

class Benchmark(modules.Benchmark):
    """
    The Benchmark class allows the definition of an exploration benchmark.
    Here we define an example exploration using stream benchmark.
    """
    name = "stream-mpi"

    keys = [
        'benchmark', 'conf_name', 'cpus', 'threads', 'rw_ratio', 'pause', 'kernel' 
        ]
    sort = [
        'benchmark', 'conf_name', 'cpus', 'threads', 'rw_ratio', 'pause', 'kernel' 
        ]

    base_curves_path = "/gpfs/scratch/bsc18/bsc18862/epi-gem5/runs/data/bw-lat-"

    
    def get_parameters(self, options):
        """
        Define benchmark parameters
        """

        # Define benchmark parameters
        parameters = dict(
            cpus = [64],
            threads = [64],
            sve_vl = [256],
            rw_ratio = [i for i in range(0, 102, 2)], 
            pause = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 100, 120, 140, 160, 180, 200, 220, 260, 300, 340, 380, 450, 550, 600, 700, 800, 900, 1000, 2000][12:],
        )

        return parameters


    def get_checkpoint_name(self, parameters: dict):

        name = 'EPI-checkpoint-{}-{}'.format(self.name, 'sve_{sve_vl}-rwratio_{rw_ratio}-pause_{pause}'.format(**parameters))
        return name

    def check_parameters(self, parameters: dict, conf_dict: dict):
        """
        Check parameter compatibility.
        If parameter combination is not compatible, return false.
        """

        if conf_dict['system']['num_cpus'] != parameters['cpus']: 
            return False

        if parameters['threads'] != parameters['cpus']:
            return False

        return True 

    def update_conf(self, parameters: dict, conf_dict: dict):
        """
        Update gem5 simulation configuration conf_dict using current iteration parameters.
        The final configuration file will be written using the updated conf_dict.
        """
        # conf_dict = super().update_conf(parameters,conf_dict)
        # conf_dict["memory"][0]["ctrl_config"]["curves_path"] = f"{self.base_curves_path}{parameters['memory_type']}"

        return conf_dict

    def get_command(self, parameters: dict, conf_dict: dict):
        """
        Construct command line to be executed, either in FS or SE mode
        """
        # Select binary
        rw_ratio = parameters['rw_ratio']
        pause = parameters['pause']

        # Select binary path based on whether running of FS mode
        if self.fs_mode:
            # Path in Linux image file
            bin_dir = "/data/bin"
        else:
            # Path in local filesystem
            bin_dir = self.binary_dir

        # Construct command line to be executed
        command = f"{bin_dir}/stream_mpi.x -p {pause} -r {rw_ratio}"

        # Return constructed command
        return command

    def get_env_dict(self, parameters: dict, conf_dict: dict):
        """
        Set environment variables used when running the benchmark executable.
        The variable env_dict is a dictionary containing environment variable names and values.
        """
        # Ged default values for env_dict
        env_dict = super().get_env_dict(parameters,conf_dict)

        # Read number of threads from parameter
        threads = parameters['threads']

        # Set OpenMP number of threads
        env_dict['OMP_NUM_THREADS'] = threads

        env_dict["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:$PATH"
        env_dict["LD_LIBRARY_PATH"] = "/data/lib/dynamic/:../lib/dynamic/:$LD_LIBRARY_PATH"

        # Return environment variables
        return env_dict

    def parse_roi(self, rdict: dict, conf_dict: dict):
        """
        Update parsed rdict with benchmark data
        """

        rdict = super().parse_roi(rdict, conf_dict)

        parameters = conf_dict['parameters']

        rdict['pause'] = parameters['pause']
        rdict['rw_ratio'] = parameters['rw_ratio']
        rdict['cpus']       = conf_dict['system']['num_cpus']
        rdict['threads']       = parameters["threads"] 
        rdict['sve_vl']     = conf_dict['cpu']['sve_vl']
        rdict['benchmark'] = self.name
        rdict["conf_name"] = parameters["conf"]
        rdict['kernel'] = self.name

        return rdict
