from pathlib import Path

from ..util import yaml_dict


def artifact_db_read(index_files: list[Path]):
    artifacts = dict()
    # Load artifact files
    for f in index_files:
        if not f.exists():
            raise SystemExit(f"Artifact index does not exist: {f}")
        l = yaml_dict.load(f)
        p = f.resolve().parent
        for arch, items in l.items():
            arch_items: list = artifacts.setdefault(arch, [])
            for i in items:
                if "path" in i and not Path(i["path"]).is_absolute():
                    i["path"] = str(p.joinpath(i["path"]))
            arch_items.extend(items)
    return artifacts


def artifact_db_add(index_file: Path, arch: str, item: dict[str, str]):
    index_db: dict[str, list[dict[str, str]]] = dict()

    if index_file.exists():
        index_db: dict[str, list[dict[str, str]]] = yaml_dict.load(index_file)

    arch_objs = index_db.setdefault(arch, [])
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

    yaml_dict.write(index_file, index_db)


def artifact_db_delete(index_file: Path, resource_path: str):
    """
    Delete resource with path resource_path from index_file
    """
    index_db: dict[str, list[dict[str, str]]] = dict()
    if index_file.exists():
        index_db = yaml_dict.load(index_file)
    # Search over all archs for the resource path
    for arch, items in index_db.items():
        idxs = [i for i, item in enumerate(items) if item["path"] == resource_path]
        for i in sorted(idxs, reverse=True):
            index_db[arch].pop(i)
    yaml_dict.write(index_file, index_db)
