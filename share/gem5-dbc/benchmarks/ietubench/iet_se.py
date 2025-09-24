from dataclasses import dataclass

from g5dbc import AbstractBenchmark, Config


@dataclass
class Params:
    nthr: int
    l1i_lat: int
    reg: str
    loopl: int
    kernel: str
    size: int
    reps: int


class iet_se(AbstractBenchmark[Params]):

    def get_varparams(self) -> dict[str, list]:
        return dict(
            # System
            nthr=[1],
            l1i_lat=[1, 2, 4],
            # Kernel
            kernel=[
                "add",
                "mul",
                "fmla",
                "fmul",
                "fadd64",
                "add_fadd64",
                "add_fmla",
                "add_fmul",
                "fadd64_fmla",
                "fadd64_fmul",
                "add_fadd64_add_fmla",
                "add_fadd64_add_fmul",
            ],
            reg=["b"],
            loopl=[1024],
            # Size
            size=[65536],
            # Reps
            reps=[5],
        )

    def filter_varparams(self, params: Params, config: Config) -> bool:
        return True

    def update_config(self, params: Params, config: Config) -> Config:
        config.caches["L1I"].latency.data = params.l1i_lat

        return config

    def get_env(self, params: Params, config: Config) -> dict:
        nthr = params.nthr
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
        bin_dir = "bin"
        bin_cmd = f"{params.kernel}_{params.reg}_{params.loopl}-m5.x"

        # Construct command line to be executed
        clock_mghz = 2600
        nloop = params.size // params.loopl
        command_opts = f"-l {nloop} -r {params.reps} -q {clock_mghz}"
        exec_command = f"{bin_dir}/{bin_cmd} {command_opts}"

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
                    row[k] = stats[col]
                    break

        row["throughput"] = params.size / row["cpu_numCycles"]
        row["latency"] = row["cpu_numCycles"] / params.size

        return row
