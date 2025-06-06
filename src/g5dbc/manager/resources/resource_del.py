from pathlib import Path

from ...util import files
from ..options import Options
from . import artifact_db


def resource_del(opts: Options):
    idx = Path(opts.artifact_index[0])
    path = Path(opts.resource_del)

    if path.is_relative_to(idx.parent):
        path = path.relative_to(idx.parent)

    artifact_db.remove(idx, path)
