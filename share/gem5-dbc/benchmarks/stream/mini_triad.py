from dataclasses import dataclass

from g5dbc import AbstractBenchmark, Config


@dataclass
class Params:
    kernel: str
    size: int
    sve_vl: int
    mem_bw: int
    reps: int


class mini_triad(AbstractBenchmark[Params]):
    P = Params

    def get_varparams(self) -> dict[str, list]:
        return dict(
            # Kernel
            kernel=["mini_triad"],
            size=[8388608, 16777216],
            # System
            sve_vl=[256, 512],
            mem_bw=[20, 40, 60, 80, 100],
            # Reps
            reps=[5],
        )

    def filter_varparams(self, params: Params, config: Config) -> bool:
        return True

    def update_config(self, params: Params, config: Config) -> Config:
        # Set system vector length
        config.system.sve_vl = params.sve_vl
        # Set memory bandwidth
        for region in config.memory.regions:
            region.model = "Simple"
            region.bandwidth = f"{params.mem_bw}GiB/s"
            region.channels = 4
        return config

    def get_env(self, params: Params, config: Config) -> dict:
        nthr = config.system.num_cpus
        env_dict = dict(
            # Execution environment should not move OpenMP threads
            OMP_PROC_BIND="true",
            OMP_DISPLAY_ENV="verbose",
            OMP_DISPLAY_AFFINITY="true",
            OMP_AFFINITY_FORMAT="%0.3L %.8n %i %.10A %.12H",
            OMP_NUM_THREADS=f"{nthr}",
            GOMP_CPU_AFFINITY=f"0-{nthr-1}" if (nthr > 1) else "0",
            SVE_VEC_LEN=int(config.system.sve_vl / 8),
        )
        return env_dict

    def get_command(self, params: Params, config: Config) -> str:
        # Path in Linux image file
        bin_dir = "/benchmarks/mini_stream/bin"
        bin_cmd = f"{params.kernel}-m5.x"

        # Construct command line to be executed
        command_opts = f"{params.size} {params.reps}"
        exec_command = f"{bin_dir}/{bin_cmd} {command_opts}"

        nthr = config.system.num_cpus
        cpu_group = f"0-{nthr-1}" if (nthr > 1) else "0"
        numa_command = f"/usr/bin/numactl -C {cpu_group} {exec_command}"

        # Return constructed command
        return numa_command

    def get_data_rows(self, params: Params, stats: dict) -> dict | list[dict]:
        row = dict()

        key_cols = dict(
            cpu_numCycles=["cpu_o3cpu_numCycles", "cpu0_o3cpu_numCycles"],
        )

        for k, cols in key_cols.items():
            for col in cols:
                if col in stats:
                    row[k] = stats[col]
                    break

        row["throughput"] = params.size / row["cpu_numCycles"]
        row["latency"] = row["cpu_numCycles"] / params.size

        return row
