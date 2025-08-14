from pathlib import Path

from ...util import dict_yaml


def read_files(index_files: list[str]) -> dict[str, list[dict[str, str]]]:
    """Read artifact index from index files

    Args:
        index_files (list[Path]): List of paths to artifact index files

    Raises:
        SystemExit: If artifact index file could not be found

    Returns:
        dict: Artifact index
    """
    artifacts = dict()
    # Load artifact files
    for f in index_files:
        fpath = Path(f)
        if not fpath.exists():
            raise SystemExit(f"Artifact index does not exist: {f}")
        l = dict_yaml.read(fpath)
        p = fpath.resolve().parent
        for arch, items in l.items():
            arch_items: list = artifacts.setdefault(arch, [])
            for i in items:
                if "path" in i and not Path(i["path"]).is_absolute():
                    i["path"] = str(p.joinpath(i["path"]))
            arch_items.extend(items)
    return artifacts


def add(index_file: Path, arch: str, items: list[dict[str, str]]):
    """Add artifact to artifact index

    Args:
        index_file (Path): Path to artifact index file
        arch (str): Artifact architecture
        item (dict[str, str]): Artifact description

    Raises:
        SystemExit: If duplicated entries found
    """

    index_db: dict[str, list[dict[str, str]]] = dict()

    if index_file.exists():
        index_db = dict_yaml.read(index_file)

    arch_objs = index_db.setdefault(arch, [])

    for item in items:
        idx = [i for i, obj in enumerate(arch_objs) if obj["path"] == item["path"]]

        match len(idx):
            case 0:
                arch_objs.append(item)
            case 1:
                arch_objs[idx[0]] = item
            case _:
                raise SystemExit(
                    f"Artifact index file {index_file} has repeated entries with same filesystem path, please correct."
                )

    dict_yaml.write(index_file, index_db)


def remove(index_file: Path, resource_path: Path):
    """Remove resource with path resource_path from index_file

    Args:
        index_file (Path): Path to artifact index file
        resource_path (str): Path to resource
    """
    index_db: dict[str, list[dict[str, str]]] = dict()
    if index_file.exists():
        index_db = dict_yaml.read(index_file)
    # Search over all archs for the resource path
    for arch, items in index_db.items():
        idxs = [i for i, item in enumerate(items) if item["path"] == str(resource_path)]
        for i in sorted(idxs, reverse=True):
            index_db[arch].pop(i)
    dict_yaml.write(index_file, index_db)
