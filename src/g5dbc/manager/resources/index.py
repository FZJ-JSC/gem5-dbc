import stat
from pathlib import Path

from ...util import sys_info
from ..options import Options
from . import artifact_db


def read_artifact_index(opts: Options) -> dict[str, list[dict[str, str]]]:

    artifacts = dict()

    if opts.artifact_index:
        artifacts = artifact_db.read_files(opts.artifact_index)
    if opts.se_exec:
        resource_path = Path(opts.se_exec).resolve()
        arch = sys_info.get_local_architecture()
        if opts.resource_arch:
            arch = opts.resource_arch
        l = artifacts.setdefault(arch, [])
        l.append(
            dict(
                bintype="EXEC",
                name=resource_path.name,
                path=str(resource_path),
                md5hash=opts.resource_hash,
                version=opts.resource_version,
                metadata=opts.resource_meta,
            )
        )

    return artifacts


def generate_artifact_index(opts: Options):
    if opts.generate_index_se:
        artifact_dir = Path(opts.generate_index_se)
        arch = sys_info.get_local_architecture()
        if opts.resource_arch:
            arch = opts.resource_arch
        items = []

        for p in artifact_dir.rglob("*"):
            if p.is_file():
                bintype = "EXEC" if p.stat().st_mode & stat.S_IXUSR else "OBJECT"
                path = str(p.relative_to(artifact_dir))
                items.append(
                    dict(
                        bintype=bintype,
                        name=str(path),
                        path=str(path),
                        md5hash="",
                        version="",
                        metadata="",
                    )
                )

        index_path = artifact_dir.joinpath("index.yaml")
        artifact_db.add(index_path, arch, items)
