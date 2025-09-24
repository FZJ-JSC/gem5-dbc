from dataclasses import dataclass

from g5dbc import AbstractBenchmark, Config


@dataclass
class Params:
    kernel: str
    size: int
    sve_vl: int
    mem_bw: int
    reps: int


class mini_triad_se(AbstractBenchmark[Params]):

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
            region.channels = 1
        return config

    def get_env(self, params: Params, config: Config) -> dict:
        return dict()

    def get_command(self, params: Params, config: Config) -> str:
        # Path in Linux image file
        bin_cmd = f"bin/{params.kernel}-m5.x"

        # Construct command line to be executed
        command_opts = f"{params.size} {params.reps}"
        exec_command = f"{bin_cmd} {command_opts}"

        # Return constructed command
        return exec_command

    def get_data_rows(self, params: Params, stats: dict) -> dict | list[dict]:
        row = dict()

        key_cols = dict(
            cpu_numCycles=["cpu_o3cpu_numCycles", "cpu0_o3cpu_numCycles"],
        )

        for k, cols in key_cols.items():
            for col in cols:
                if col in stats:
                    row[k] = int(stats[col])
                    break

        row["throughput"] = params.size / row["cpu_numCycles"]
        row["latency"] = row["cpu_numCycles"] / params.size

        return row
