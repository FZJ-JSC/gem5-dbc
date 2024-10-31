import re

from modules.stats.parsers import util

def parse_ruby_routers(key:str, val: str, r: dict, links_dict: dict):

    p = r"system\.ruby\.network\.int_links(\d+)\.(dst|src)_node\.buffer_(reads|writes)"
    m = re.match(p, key)
    if m:
        linkId    = int(m.group(1))
        direction = m.group(2)
        operation = m.group(3)

        if (linkId in links_dict):
            routerId = links_dict[linkId][direction]
            r = util.accumulate_num_col(f"network_router{routerId}_{operation}", val, r)
        
        r = util.accumulate_num_col(f"network_link{linkId}_{direction}_{operation}", val, r)

        return r

    return r
