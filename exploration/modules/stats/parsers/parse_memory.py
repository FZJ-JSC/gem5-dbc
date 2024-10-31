import re

from modules.stats.parsers import util

def parse_memory(key:str, val: str, r: dict):

    # Data bus utilization in percentage
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(busUtil)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    # Misc stuff for BwLatCtrl 
    # system.mem_ctrls1.totalDispatchedLatency 
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(totalDispatchedLatency)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    # system.mem_ctrls1.latencyDispatchedCount
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(latencyDispatchedCount)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    # system.mem_ctrls1.totalRequestedBandwidth
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(totalRequestedBandwidth)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    # system.mem_ctrls1.bandwidthRequestedCount
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(bandwidthRequestedCount)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    p = r"system\.mem_ctrls(\d*)(.dram)?\.(numReads)::total$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    p = r"system\.mem_ctrls(\d*)(.dram)?\.(numWrites)::total$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r
    # Controller Latency
    # system.mem_ctrls1.dram.avgMemAccLat 
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(avgMemAccLat)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_sum_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    # Data bus utilization in percentage
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(busUtilRead|busUtilWrite)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r

    # Memory bandwidth
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(avgRdBW|avgWrBW|peakBW|pageHitRate)$"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r
    

    # Memory bandwidth and bytes transfered
    p = r"system\.mem_ctrls(\d*)(.dram)?\.(bwRead|bwWrite|bwTotal|numReads|numWrites|bytesRead|bytesWritten|bytesPerActivate)::total"
    m = re.match(p, key)
    if m:
        ctrl_name = m.group(1)
        ctrl = int(ctrl_name) if ctrl_name != "" else 0
        name = m.group(3)
        r = util.accumulate_num_col(f"mem_ctrls_{name}", val, r)
        r = util.accumulate_num_col(f"mem_ctrl{ctrl}_{name}", val, r)

        return r
        

    return r
