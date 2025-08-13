from pathlib import Path

from ..options import Options
from . import artifact_db


def read_artifact_index(opts: Options) -> dict[str, list[dict[str, str]]]:

    artifacts = dict()

    if opts.artifact_index:
        artifacts = artifact_db.read_files(opts.artifact_index)

    return artifacts
