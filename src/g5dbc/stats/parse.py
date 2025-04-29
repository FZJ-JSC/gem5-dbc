import re
from pathlib import Path
from typing import Any, Iterator


def parse_number_str(x: str | None, default="") -> int | float | str:
    if x is None:
        return default
    if x is not None:
        try:
            return int(x, 0)
        except:
            pass
        try:
            return float(x)
        except:
            pass
    return str(x)


def parse_gem5_histogram(line: str) -> list[tuple[int, int | float | str]]:
    r = re.compile(r"\|\s*([+-.\d]+)")
    h = [
        (n, v) for n, v in enumerate([parse_number_str(n) for n in re.findall(r, line)])
    ]
    return h


def parse_gem5_sparse_histogram(
    line: str,
) -> list[tuple[int | float | str, int | float | str]]:
    r = re.compile(r"\|\s*([+-.\d]+),([+-.\d]+)")
    h = [(parse_number_str(n[0]), parse_number_str(n[1])) for n in re.findall(r, line)]
    return h


def parse_gem5_sparse_list(line: str) -> list[list[tuple[int | float | str, ...]]]:
    r1 = line.split("|")
    r2 = [e.split(";") for e in r1]
    r3 = [
        [tuple([parse_number_str(n) for n in e2.split(",")]) for e2 in e1[:-1]]
        for e1 in r2[1:]
    ]
    return r3


def parse_gem5_key(key: str) -> tuple[list[str], str]:
    r1 = re.compile(r"_?([0-9]+)[_\.]")
    m1 = lambda m: f".{m[1]}."
    l1 = re.sub(r1, m1, key)
    r2 = re.compile(r"([0-9]+)(::|$)")
    m2 = lambda m: f".{m[1]}{m[2] or ''}"
    l2 = re.sub(r2, m2, l1)
    s = l2.split("::")
    p = s[0].split(".")
    k = "" if len(s) == 1 else s[1]
    return (p, k)


def normalize_gem5_stats_line(line: str) -> tuple[list[str], str, Any]:
    s = line.split()
    p, k = parse_gem5_key(s[0])
    c = s[1][:1]
    if k == "":
        if c == "|":
            v = list(parse_gem5_histogram(line))
            k = "list"
        else:
            v = parse_number_str(s[1])
    else:
        if c == "|" and k in [
            "values",
        ]:
            v = list(parse_gem5_sparse_histogram(line))
        elif c == "|" and k in [
            "selected",
        ]:
            v = parse_gem5_sparse_list(line)
        else:
            v = parse_number_str(s[1])
    # Catch buggy stats.txt
    v = 0 if v == "#" or v == "(Unspecified)" else v
    return (p, k, v)


def stats_line_generator(
    stats_file: Path,
    max_roi_id=5,
) -> Iterator[tuple[int, list[str], str, Any]]:
    """Iterate gem5 statistics file line by line

    Args:
        stats_file (Path): gem5 statistics output file
        max_roi_id (int, optional): Maximum number of ROIs to parse. Defaults to 5.

    Yields:
        Iterator[tuple[int, list[str], str, Any]]: Returns a tuple of 4 elements: ROI number, performance counter path, performance counter key and performance counter value.
    """

    with open(stats_file) as f:
        roi_id = 0
        is_roi = False
        for line in f:
            if line and line.strip():
                if roi_id >= max_roi_id:
                    break
                m = re.match("-", line)
                if m:
                    roi_id = roi_id + 1 if is_roi else roi_id
                    is_roi = not is_roi
                    continue
                # r = d.setdefault(roi_id, init_config_parameters(config, roi_id))
                path, key, val = normalize_gem5_stats_line(line)
                yield (roi_id, path, key, val)
