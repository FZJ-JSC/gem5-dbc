import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from ..config import Config
from ..util import iterate

T = TypeVar("T")


class AbstractBenchmark(ABC, Generic[T]):
    """
    Abstract Benchmark
    """

    def __init__(
        self,
        workspace_dir: Path,
        user_data_dir: Path,
        generated_dir="work",
        parsed_dir="parsed",
    ):
        self.workspace_dir = workspace_dir
        self.user_data_dir = user_data_dir
        self.generated_dir = workspace_dir.joinpath(self.name, generated_dir)
        self.parsed_dir = workspace_dir.joinpath(self.name, parsed_dir)

    @staticmethod
    @abstractmethod
    def P(**kwargs) -> T:
        """Return instance of benchmark parameter class T

        Args:
            **kwargs: Parameter class constructor arguments

        Returns:
            T: Instance of benchmark parameter class
        """

    @abstractmethod
    def get_command(self, params: T, config: Config) -> str:
        """Return command to execute

        Args:
            params (T): Current parameter combination
            config (Config): Updated benchmark configuration

        Returns:
            str: Command to execute as benchmark
        """

    @abstractmethod
    def get_env(self, params: T, config: Config) -> dict:
        """Return shell environment for benchmark

        Args:
            params (T): Current parameter combination
            config (Config): Updated benchmark configuration

        Returns:
            dict: Dictionary of environment variables
        """

    @abstractmethod
    def get_varparams(self) -> dict[str, list]:
        """Return a list of iterateble parameters

        Returns:
            dict[str, list]: list of iterateble parameters
        """

    @abstractmethod
    def filter_varparams(self, params: T) -> bool:
        """Return True if given parameter combination is valid

        Args:
            params (T): Current parameter combination

        Returns:
            bool: Return True if current parameter combination is valid
        """

    @abstractmethod
    def update_config(self, params: T, config: Config) -> Config:
        """Update configuration from given parameters

        Args:
            params (T): Current parameter iteration
            config (Config): Initial configuration

        Returns:
            Config: Updated configuration from current parameter iteration
        """

    @abstractmethod
    def get_data_rows(self, params: T, stats: dict) -> dict | list[dict]:
        """Return a single data row or multiple data rows to be written

        Args:
            params (T): _description_
            stats (dict): _description_

        Returns:
            dict | list[dict]: Return single or multiple data rows
        """

    @property
    def name(self):
        """
        Benchmark name
        """
        return self.__class__.__name__

    def get_bench_command(self, config: Config) -> str:
        """
        Update Config
        """
        return self.get_command(self.P(**config.parameters), config)

    def get_env_vars(self, config: Config) -> dict:
        """
        Update Config
        """
        return self.get_env(self.P(**config.parameters), config)

    def get_parameter_list(self, config: Config) -> list[dict]:
        """
        Get filtered parameter list
        """
        parameters = [
            p
            for p in iterate(self.get_varparams())
            if self.filter_varparams(self.P(**p))
        ]
        assert len(parameters) > 0
        return parameters

    def get_updated_config(self, config: Config) -> Config:
        """
        Update Config
        """
        return self.update_config(self.P(**config.parameters), config)

    def get_column_keys(self, config: Config) -> dict:
        """
        Return dictionary for parsed parameter columns
        """
        params_dict = dict(**config.parameters)

        return params_dict

    def get_data_rows_from_stats(self, stats: dict) -> list[dict]:
        params = dict([(k, stats[k]) for k in self.get_varparams().keys()])
        r = self.get_data_rows(self.P(**params), stats)
        if isinstance(r, dict):
            r = [r]
        for e in r:
            e.update(
                dict(
                    bench_name=stats["bench_name"],
                    bench_id=stats["bench_id"],
                    roi_id=stats["roi_id"],
                    **params,
                )
            )
        return r

    def parse_output_log(self, output_file: Path) -> dict:
        if not output_file.exists():
            return dict()
        output_log = output_file.read_text()
        cdict: dict = dict(
            aborted=dict(), links=dict(), router=dict(), network=dict(links=list())
        )

        for l in iter(output_log.splitlines()):
            p = r"BEGIN LIBC BACKTRACE"
            m = re.search(p, l)
            if m:
                cdict["aborted"]["backtrace"] = True
                continue
            else:
                cdict["aborted"]["backtrace"] = False

        return cdict

    def parse_stdout_log(self, stdout_file: Path) -> dict:
        rdict = dict()
        return rdict
