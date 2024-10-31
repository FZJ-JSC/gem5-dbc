import re

from modules.stats.parsers import util

def parse_ruby_cache(key:str, val: str, r: dict):

    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.cache\.m_(demand)_(accesses|hits|misses)"
    m = re.match(p, key)
    if m:
        cpu_Id = int(m.group(1))
        ncache = m.group(2)
        demand = m.group(3)
        access = m.group(4)
        cols = [
            f"cpu{cpu_Id}_{ncache}_{demand}_{access}",
            f"caches_{ncache}_{demand}_{access}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.cache\.num(Data|Tag)Array(Reads|Writes)"
    m = re.match(p, key)
    if m:
        cpu_Id = int(m.group(1))
        ncache = m.group(2)
        demand = m.group(3)
        access = m.group(4)
        cols = [
            f"cpu{cpu_Id}_{ncache}_{demand}_{access}",
            f"caches_{ncache}_{demand}_{access}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.(dat|req|rsp|snp)(In|Out|Rdy)\.m_(buf_msgs|stall_time)"
    m = re.match(p, key)
    if m:
        cpu_Id  = int(m.group(1))
        ncache  = m.group(2)
        nport   = m.group(3)
        in_out  = m.group(4)
        average = m.group(5)
        cols = [
            f"cpu{cpu_Id}_{ncache}_{nport}{in_out}_avg_{average}",
            f"caches_{ncache}_{nport}{in_out}_avg_{average}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    p = r"system\.ruby\.hnf(\d+)\.cntrl\.cache\.m_(demand)_(accesses|hits|misses)"
    m = re.match(p, key)
    if m:
        hnf_Id = int(m.group(1))
        demand = m.group(2)
        access = m.group(3)
        cols = [
            f"HNF{hnf_Id}_{demand}_{access}",
            f"HNF_{demand}_{access}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    p = r"system\.ruby\.hnf(\d+)\.cntrl\.cache\.num(Data|Tag)Array(Reads|Writes)"
    m = re.match(p, key)
    if m:
        hnf_Id = int(m.group(1))
        demand = m.group(2)
        access = m.group(3)
        cols = [
            f"HNF{hnf_Id}_{demand}_{access}",
            f"HNF_{demand}_{access}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    p = r"system\.ruby\.hnf(\d+)\.cntrl\.(dat|req|rsp|snp)(In|Out)\.avg_(buf_msgs|stall_time)"
    m = re.match(p, key)
    if m:
        hnf_Id = int(m.group(1))
        in_out = m.group(2)
        average = m.group(3)
        cols = [
            f"HNF{hnf_Id}_{in_out}_avg_{average}",
            f"HNF_{in_out}_avg_{average}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    return r
