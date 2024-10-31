import re

from modules.stats.parsers import util
from modules.stats.parsers.float_ops import float_ops

def parse_cpu(key:str, val: str, r: dict, simdw = 4):

    # CPU stats
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.(\w+)$"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        label = m.group(2)
        cols = [
            f"CPU_{label}_cpu{cpuId}",
            f"CPU_{label}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        
        return r

    # Number of issued instructions
    # Attempts to use FU when none available
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.(numIssuedDist|statFuBusy)::(\d+|\w+)$"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        label = m.group(2)
        stats = m.group(3)

        v = util.capture_number(val)

        cols = [
            f"CPU_{label}_cpu{cpuId}_{stats}",
            f"CPU_{label}_{stats}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, v, r)
        
        return r

    # CPU pipeline
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.(branchPred|commit|decode|fetch|lsq0|rename|rob)\.(\w+)$"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        label = m.group(2)
        ctgry = m.group(3)
        # capture number
        v = util.capture_number(val)

        label = label.upper()

        cols = [
            f"CPU_{label}_cpu{cpuId}_{ctgry}",
            f"CPU_{label}_{ctgry}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, v, r)
        
        return r


    # Class of committed instructions: Int
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.commit\.committedInstType_0::(Int)(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        IntId = m.group(2)
        ci_Id = m.group(3)
        # capture number
        v = util.capture_number(val)

        cols = [
            f"CI_{IntId}_cpu{cpuId}_{ci_Id}",
            f"CI_{IntId}_{ci_Id}",
            f"CI_{IntId}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, v, r)
        
        return r

    # Class of committed instructions: Floating point
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.commit\.committedInstType_0::(Simd|Float)(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        vecId = m.group(2)
        ci_Id = m.group(3)
        # capture number
        v = util.capture_number(val)

        cols = [
            f"{vecId}Ops",
            f"CI_FP_cpu{cpuId}_{vecId}{ci_Id}",
            f"CI_FP_cpu{cpuId}",
            f"CI_FP_{vecId}{ci_Id}",
            f"CI_FP_{vecId}",
            f"CI_FP"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, v, r)

        # Lookup FLOPS
        flops = float_ops(f"{vecId}{ci_Id}", simdw)*util.parse_number(v)

        cols = [
            f"CI_FLOPS_cpu{cpuId}",
            f"CI_FLOPS"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, flops, r)
        
        return r

    # Class of committed instructions: Memory
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.commit\.committedInstType_0::(Float)?(Mem)(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        IntId = m.group(2) if m.group(2) else ""
        #IntId = m.group(3)
        ci_Id = m.group(4)
        # capture number
        v = util.capture_number(val)

        cols = [
            f"CI_Mem_cpu{cpuId}_{IntId}{ci_Id}",
            f"CI_Mem_cpu{cpuId}",
            f"CI_Mem_{IntId}{ci_Id}",
            f"CI_Mem",
        ]
        
        for c in cols:
            r = util.accumulate_num_col(c, v, r)
        
        return r


    # Instruction pipeline
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.statIssuedInstType_0::(Int|Simd|Float)(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        ctgry = m.group(2)
        instr = m.group(3)
        # capture number
        v = util.capture_number(val)

        cols = [
            f"FU_cpu{cpuId}_{ctgry}{instr}",
            f"FU_cpu{cpuId}_{ctgry}",
            f"FU_{ctgry}"
        ]

        for c in cols:
            r = util.accumulate_num_col(c, v, r)

        if float_ops(f"{ctgry}{instr}") > 0 :
            c = 'FU_FloatSimd'
            r = util.accumulate_num_col(c, v, r)
        
        return r


    # Instruction pipeline
    p = r"system\.(?:switch_)?cpus?([0-9]*)\.statIssuedInstType_0::(Float)?(Mem)(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        ctgry = m.group(2) if m.group(2) else ""
        instr = m.group(4)
        # capture number
        v = util.capture_number(val)

        cols = [
            f"FU_cpu{cpuId}_{ctgry}Mem{instr}",
            f"FU_cpu{cpuId}_{ctgry}Mem",
            f"FU_Mem"
        ]

        for c in cols:
            r = util.accumulate_num_col(c, v, r)
        
        return r


    # Memory dependence unit
    p = r"system\.(?:switch_)?cpus?(\d*)\.MemDepUnit__(\d*)\.(conflicting|inserted)(Loads|Stores)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0

        label = m.group(3)
        operation = m.group(4)

        cols = [
            f"CPU_MemDep{label}_cpu{cpuId}_{operation}",
            f"CPU_MemDep{label}_{operation}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)

        return r


    # Distribution of cycle latency between the first time a load is issued and its completion
    p = r"system\.(?:switch_)?cpus?(\d*)\.lsq(\d+)\.(loadToUse)::([-+]?\d+|samples)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1)) if m.group(1) else 0
        lsqId = int(m.group(2)) if m.group(2) else 0
        label = m.group(3)
        bucket = m.group(4)

        cols = []
        if bucket == "samples":
            cols = [
                f"CPU_{label}_cpu{cpuId}_{bucket}",
                f"CPU_{label}_{bucket}",
            ]
            nval = val
            accf = util.accumulate_num_col
        else:
            cols = [
                f"CPU_{label}_cpu{cpuId}",
                f"CPU_{label}",
            ]
            nval = ((int(cpuId),int(bucket)),int(val))
            accf = util.accumulate_dict_col

        for c in cols:
            r = accf(c, nval, r)
        return r

    return r
