from pathlib import Path
import re

def parse_number_text(txt: str|None, default='') -> int|float|str:
    if txt is None:
        return default
    if txt is not None:
        try:
            return int(txt)
        except ValueError:
            pass
        try:
            return float(txt)
        except ValueError:
            pass
    return str(txt)

def parse_gem5_histogram(line: str):
    r = re.compile(r"\|\s*([+-.\d]+)")
    h  = [(n,v) for n,v in enumerate([parse_number_text(n) for n in re.findall(r,line)])]
    return h

def parse_gem5_sparse_histogram(line: str):
    r = re.compile(r"\|\s*([+-.\d]+),([+-.\d]+)")
    h  = [(parse_number_text(n[0]),parse_number_text(n[1])) for n in re.findall(r,line)]
    return h

def parse_gem5_key(key: str):
    """_summary_

    Args:
        key (str): _description_

    Returns:
        _type_: _description_
    """
    r1 = re.compile(r"_?([0-9]+)[_\.]")
    m1 = lambda m: f".{m[1]}."
    l1 = re.sub(r1, m1, key)
    r2 = re.compile(r"([0-9]+)(::|$)")
    m2 = lambda m: f".{m[1]}{m[2] or ''}"
    l2 = re.sub(r2, m2, l1)
    s = l2.split("::")
    p = s[0].split(".")
    k = None if len(s) == 1 else s[1]
    return (p,k)

def normalize_gem5_stats_line(line: str):
    s = line.split()
    p, k = parse_gem5_key(s[0])
    c = s[1][:1]
    if k is None:
        if c == "|":
            v = list(parse_gem5_histogram(line))
            k = "list"
        else:
            v = parse_number_text(s[1])
    else:
        if c == "|" and k == "values":
            v = list(parse_gem5_sparse_histogram(line))
        else:
            v = parse_number_text(s[1])
    # Catch buggy stats.txt    
    v = 0 if v == "#" or v == "(Unspecified)" else v
    return p,k,v

def stats_line_generator(stats_file: Path, max_roi_id=5):
    with open(stats_file) as f:
        roi_id=0
        is_roi=False
        for line in f:
            if line and line.strip():
                if roi_id >= max_roi_id:
                    break
                m = re.match("-", line)
                if m:
                    roi_id = roi_id + 1 if is_roi else roi_id
                    is_roi = not is_roi
                    continue
                #r = d.setdefault(roi_id, init_config_parameters(config, roi_id))
                path, key, val = normalize_gem5_stats_line(line)
                yield (roi_id, path, key, val)
