import re
from modules.stats.parsers import util

def parse_prefetcher(key:str, val: str, r: dict):
    
    p = r"system.cpu(\d+).(\w+).prefetcher.prefetcher.pf(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        cache = m.group(2)
        label = m.group(3)
        cols = [
            f"cpu{cpuId}_pf{cache}_{label}",
            f"cpu_pf{cache}_{label}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
    
    p = r"system.cpu(\d+).(\w+).cache.prefetch_(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        cache = m.group(2)
        label = m.group(3)
        cols = [
            f"cpu{cpuId}_pf{cache}_{label}",
            f"cpu_pf{cache}_{label}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
    
    p = r"system.cpu(\d+).(\w+).prefetchQueue.(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        cache = m.group(2)
        label = m.group(3)
        cols = [
            f"cpu{cpuId}_pf{cache}_{label}",
            f"cpu_pf{cache}_{label}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
    

    return r
