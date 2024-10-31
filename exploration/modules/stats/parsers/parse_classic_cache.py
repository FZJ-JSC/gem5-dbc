import re

from modules.stats.parsers import util

def parse_classic_cache(key:str, val: str, r: dict):

    p = r"system\.cpu([0-9]*)\.(l2cache|dcache|icache).overall_(accesses|misses|hits|miss_rate)::total"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        cache = "l2" if (m.group(2) == "l2cache") else m.group(2)
        access = m.group(3)
        cols = [
            f"{cache}{cpuId}_{access}",
            f"{cache}_{access}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    p = r"system\.l3([0-9]*)\.overall_(accesses|misses|hits|miss_rate)::total"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        access = m.group(2)
        cols = [
            f"slc{cpuId}_{access}",
            f"slc_{access}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

    return r
