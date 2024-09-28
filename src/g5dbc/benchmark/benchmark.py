from abc import ABC, abstractmethod
import re
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
    def get_varparams(self) -> dict[str,list]:
        """
        Return iteratable parameters
        """

    @abstractmethod
    def filter_varparams(self, config: Config, params: dict) -> bool:
        """
        Filter Config
        """

    @abstractmethod
    def get_config(self, config: Config, params: dict) -> Config:
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

        """
        parameters = [p for p in iterate(self.get_varparams()) if self.filter_varparams(config, p)]
        assert(len(parameters) > 0)
        return parameters


    def parse_output_log(self, output_file: Path) -> dict:
        output_log = output_file.read_text()
        cdict : dict = dict(
            aborted = dict(),
            links = dict(),
            router = dict(),
            network = dict(
                links = list()
            )
        )

        for l in iter(output_log.splitlines()):
            p = r"BEGIN LIBC BACKTRACE"
            m = re.search(p, l)
            if m:
                cdict["aborted"]["backtrace"] = True
                continue
            else:
                cdict["aborted"]["backtrace"] = False

            p = r"R(\d+)\.L(\d+)\.R(\d+)"
            m = re.search(p, l)
            if m:
                src  = int(m.group(1))
                link = int(m.group(2))
                dst  = int(m.group(3))
                cdict["links"][link] = {}
                cdict["links"][link]["src"] = src
                cdict["links"][link]["dst"] = dst
                continue

            p = r"EXT.(\w+)\.(\d+)\.(\w+)\.L(\d+)\.R(\d+)"
            m = re.search(p, l)
            if m:
                node   = m.group(1)
                ctrlId = int(m.group(2))
                ctrl   = m.group(3)
                link   = int(m.group(4))
                router = int(m.group(5))

                cdict["router"][router] = dict(
                    node=node
                )

                continue

            p = r"make(\w+)Link src=(\d+) (\w+)Id=(\d+) linkId=(\d+) dest=(\d+) (\w+)Id=(\d+)"
            m = re.search(p, l)
            if m:
                item = dict(
                    linkType = m.group(1),
                    src = int(m.group(2)),
                    srcType = m.group(3),
                    srcId = int(m.group(4)),
                    linkId = int(m.group(5)),
                    dst = int(m.group(6)),
                    dstType = m.group(7),
                    dstId = int(m.group(8)),
                )

                cdict["network"]["links"].append(item)

                continue

        return cdict

    def parse_stdout_log(self, stdout_file: Path) -> dict:
        rdict = dict()
        return rdict