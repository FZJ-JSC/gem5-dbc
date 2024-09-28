from dataclasses import dataclass

from g5dbc import AbstractBenchmark
from g5dbc import Config

@dataclass
class Params:
    sve_vl: int
    mem_lat: int
    kernel: str
    size: int
    reps: int

class stream(AbstractBenchmark):

    def get_varparams(self) -> dict[str,list]:
        """Return a list of iterateble parameters

        Returns:
            dict[str,list]: list of iterateble parameters
        """
        return dict(
            sve_vl   = [256, 512],
            mem_lat  = [5,10,50,100],
            # Kernel
            kernel = ["triad"],
            size = [int(3E5),int(8E5),],
            # Reps
            reps = [5,],
        )

    def filter_varparams(self, conf: Config, params: dict) -> bool:
        """Return True if configuration is valid

        Args:
            conf (Config): Current benchmark configuration

        Returns:
            bool: True if benchmark configuration is valid, False otherwise
        """
        p = Params(**params)

        return True

    def get_config(self, conf: Config, params: dict) -> Config:
        """Update configuration based on given parameters

        Args:
            conf (Config): Current benchmark configuration

        Returns:
            Config: Updated configuration
        """
        p = Params(**params)

        conf.system.sve_vl = p.sve_vl
        for region in conf.memory.regions:
            region.latency = f"{p.mem_lat}ns"

        return conf

    def get_env(self, conf: Config) -> dict:
        """Return shell environment for benchmark

        Args:
            conf (Config): Current benchmark configuration

        Returns:
            dict: Dictionary of environment variables
        """
        sve_vl   = conf.system.sve_vl
        num_cpus = conf.system.num_cpus

        env_dict = dict(
            # Execution environment should not move OpenMP threads
            OMP_PROC_BIND = "true",
            OMP_DISPLAY_ENV = "verbose",
            OMP_DISPLAY_AFFINITY = "true",
            OMP_AFFINITY_FORMAT = "%0.3L %.8n %i %.10A %.12H",
            OMP_NUM_THREADS = f"{num_cpus}",
            GOMP_CPU_AFFINITY = f"0-{num_cpus-1}" if (num_cpus>1) else "0",
            SVE_VEC_LEN = int(sve_vl/8)
        )
        return env_dict

    def get_command(self, conf: Config) -> str:
        """Return command to execute

        Args:
            conf (Config): Current benchmark configuration

        Returns:
            str: Command to execute
        """
        params = Params(**conf.parameters)

        # Path in Linux image file
        bin_dir = "/benchmarks/bin"

        size = conf.system.num_cpus*params.size

        # Construct command line to be executed
        command = f"{bin_dir}/mini_{params.kernel}-m5.x {size} {params.reps}"

        # Return constructed command
        return command
