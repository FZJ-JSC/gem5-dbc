import re

from modules.stats.parsers import util

def parse_ruby_network_sparse_histogram(key:str, val: str, r: dict):

    # network latency histogram
    p = r"system\.ruby\.network\.router_(flit)_(network|queueing)_(latency_hist)_vnet(\d+)::(\d+|samples)"
    m = re.match(p, key)
    if m:
        flit = m.group(1)
        netw = m.group(2)
        label  = m.group(3)
        vnet   = int(m.group(4))
        bucket = m.group(5)

        cols = []
        if bucket == "samples":
            cols = [
                f"mesh_{flit}_{netw}_{label}_vnet{vnet}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"mesh_{flit}_{label}_vnet{vnet}",
            ]
            nval = ((netw,int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r

    # network latency histogram
    p = r"system\.ruby\.network\.(network_latencies)_vnet(\d+)_(link|router|nis)(\d+)::(\d+|samples)"
    m = re.match(p, key)
    if m:
        group = m.group(1)
        vnet = int(m.group(2))
        ctrl = m.group(3)
        ctrlId  = int(m.group(4))
        bucket = m.group(5)

        cols = []

        if bucket == "samples":
            cols = [
                f"mesh_{group}_vnet{vnet}_{ctrl}{ctrlId}_{bucket}",
                f"mesh_{group}_vnet{vnet}_{ctrl}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"mesh_{group}_vnet{vnet}_{ctrl}{ctrlId}",
                f"mesh_{group}_vnet{vnet}_{ctrl}",
            ]
            nval = ((ctrlId,int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r


    # network latency histogram
    p = r"system\.ruby\.network\.(network_latencies_ni_src_delay)_vnet(\d+)_(nis)(\d+)::(\d+|samples)"
    m = re.match(p, key)
    if m:
        group = m.group(1)
        vnet = int(m.group(2))
        ctrl = m.group(3)
        ctrlId  = int(m.group(4))
        bucket = m.group(5)

        cols = []

        if bucket == "samples":
            cols = [
                f"mesh_{group}_vnet{vnet}_{ctrl}{ctrlId}_{bucket}",
                f"mesh_{group}_vnet{vnet}_{ctrl}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"mesh_{group}_vnet{vnet}_{ctrl}{ctrlId}",
                f"mesh_{group}_vnet{vnet}_{ctrl}",
            ]
            nval = ((ctrlId,int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r


    # network latency histogram
    p = r"system\.ruby\.network\.(network_latencies_routers_src_dst)_(network|queueing)_vnet(\d+)_(router)(\d+)_(router)(\d+)::(\d+|samples)"
    m = re.match(p, key)
    if m:
        group1 = m.group(1)
        group2 = m.group(2)
        vnet = int(m.group(3))
        ctrl1 = m.group(4)
        ctrl1Id  = int(m.group(5))
        ctrl2 = m.group(6)
        ctrl2Id  = int(m.group(7))
        bucket = m.group(8)

        group = f"{group1}_{group2}"
        cols = []

        if bucket == "samples":
            cols = [
                f"mesh_{group}_vnet{vnet}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"mesh_{group}_vnet{vnet}",
            ]
            nval = ((ctrl1Id,ctrl2Id,int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r

    # Network Interface Assignment
    p = r"system\.ruby\.network\.(net_ifs_assigned)_ni(\d+)_vnet(\d+)::([-+]?\d+|samples)"
    m = re.match(p, key)
    if m:
        group  = m.group(1)
        ctrl1  = int(m.group(2))
        vnet   = int(m.group(3))
        bucket = m.group(4)

        cols = []
        if bucket == "samples":
            cols = [
                f"mesh_{group}_vnet{vnet}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"mesh_{group}_vnet{vnet}",
            ]
            nval = ((ctrl1,int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r

    # Router Assignment
    p = r"system\.ruby\.network\.(routers)_(\w+)_router(\d+)_vnet(\d+)_inLink(\d+)::([-+]?\d+|samples)"
    m = re.match(p, key)
    if m:
        group  = m.group(1)
        label  = m.group(2)

        ctrl1  = int(m.group(3))
        vnet   = int(m.group(4))
        ctrl2  = int(m.group(5))
        bucket = m.group(6)

        cols = []
        if bucket == "samples":
            cols = [
                f"mesh_{group}_{label}_vnet{vnet}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"mesh_{group}_{label}_vnet{vnet}",
            ]
            nval = ((ctrl1,ctrl2,int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r

    return r
