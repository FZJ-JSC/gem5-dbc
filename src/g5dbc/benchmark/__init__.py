import re
from abc import ABC, abstractmethod
from pathlib import Path

from ..config import Config
from ..util import iterate


class AbstractBenchmark(ABC):
    """
    Abstract Benchmark
    """

    def get_name(self) -> str:
        """
        Get benchmark name
        """
        return self.__class__.__name__

    @abstractmethod
    def get_command(self, config: Config) -> str:
        """
        Get benchmark command
        """

    @abstractmethod
    def get_env(self, config: Config) -> dict:
        """
        Get benchmark environment variables
        """

    @abstractmethod
    def get_varparams(self) -> dict[str, list]:
        """
        Return iteratable parameters
        """

    @abstractmethod
    def filter_varparams(self, params: dict) -> bool:
        """
        Filter Config
        """

    @abstractmethod
    def update_config(self, params: dict, config: Config) -> Config:
        """
        Update Config
        """

    def parse_config(self, config: Config) -> dict:
        """
        Return dictionary for parsed parameter columns
        """
        params_dict = dict(**config.parameters)

        return params_dict

    def get_parameter_list(self, config: Config) -> list[dict]:
        """
        Get filtered parameter list
        """
        parameters = [
            p for p in iterate(self.get_varparams()) if self.filter_varparams(p)
        ]
        assert len(parameters) > 0
        return parameters

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
