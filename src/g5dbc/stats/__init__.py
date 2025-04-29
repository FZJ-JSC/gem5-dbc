import re
from abc import ABC, abstractmethod
from pathlib import Path

import yaml

from . import parse


class StatsParser(ABC):
    """
    Statistics Parser
    """

    def __init__(self, parser_re_dir: Path):
        parser_conf = [f for f in parser_re_dir.iterdir() if f.suffix == ".yaml"]
        self.regexes: list[tuple[str, list[str]]] = []
        for file in parser_conf:
            with file.open("r") as stream:
                self.regexes.extend(yaml.safe_load(stream))

    def parse_stats(
        self, stats_params: dict, parsed_output: dict, stats_file: Path
    ) -> dict[int, dict[str, int | float | list]]:
        max_roi_id = 5
        parsed_rois: dict[int, dict] = dict()
        for roi_id, path, key, val in parse.stats_line_generator(stats_file):
            s = ".".join(path)
            for r, labels in self.regexes:
                m = re.fullmatch(r, s)
                if m:
                    for l in labels:
                        g = [parse.parse_number_str(k) for k in m.groups()]
                        c = l.format(*g)
                        roi_cols = parsed_rois.setdefault(roi_id, dict())
                        self.update_column(roi_cols, c, key, val)
                    break

        for roi_id, parsed_roi in parsed_rois.items():
            parsed_roi.update(dict(**stats_params, roi_id=roi_id))
            self.update_terminal_output(parsed_roi, parsed_output)

        return parsed_rois

    @abstractmethod
    def update_column(self, r: dict, c: str, key: str, val) -> dict:
        """
        Update statistics column
        """

    @abstractmethod
    def update_terminal_output(self, r: dict, parsed_output: dict) -> dict:
        """
        Update statistics with information from terminal output
        """
