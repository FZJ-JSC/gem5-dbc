import re

from modules.util import parse_number

def capture_number(txt: str):
    p = r"([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"
    m = re.match(p, txt)
    if m:
        num = m.group(1)
        return num
    else:
        return txt

def rm_comments(line: str, comment: str  = '#'):
    nline = str(line)
    p = nline.find(comment)
    if p >= 0:
        nline = nline[:p]
    p = nline.find("(Unspecified)")
    if p >= 0:
        nline = nline[:p]
    return nline.strip()


def gem5_key_value(line:str):
    tok = rm_comments(line).split()
    k = tok[0]
    v = ' '.join(tok[1:])
    return k,v

def accumulate_num_col(col_name: str, col_value: str, cols: dict):
    cols[col_name] = parse_number(col_value) + cols.get(col_name, 0)
    return cols

def accumulate_dict_col(col_name: str, col_value, cols: dict):
    if col_name in cols:
        cols[col_name].update([col_value])
    else:
        cols[col_name] = dict([col_value])
    return cols

def parse_gem5_histogram(val: str):
    regx = r"\|\s*([+-.\d]+)"
    res  = enumerate(re.findall(regx,val))
    return res

def parse_file(filename: str, parsers = []):
    r = dict()
    with open(filename) as f:
        for line in f:
            k,v = gem5_key_value(line)
            for p in parsers:
                r = p(r,k,v)
    return r
