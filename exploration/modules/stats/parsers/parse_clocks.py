import re

from modules.stats.parsers.util import parse_number

def parse_clocks(key:str, val: str, r: dict):

    p = r"hostSeconds"
    m = re.match(p, key)
    if m:
        r["hostSeconds"] = parse_number(val)
        return r

    p = r"system\.(ruby)?\.?(cpu)?_?(clk_domain)\.clock"
    m = re.match(p, key)
    if m:
        name = "system"
        name = "ruby" if m.group(1) else name
        name = "cpu"  if m.group(2) else name
        r[f"{name}_clock"] = parse_number(val)
        return r

    p = r"(sim|host)(Seconds|Ticks|Freq|Insts|Ops|TickRate|Memory|InstRate|OpRate)"
    m = re.match(p, key)
    if m:
        name = m.group(1)
        metr = m.group(2)
        r[f"{name}{metr}"] = parse_number(val)
        return r

    return r
