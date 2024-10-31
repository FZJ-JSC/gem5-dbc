import re

from modules.stats.parsers import util


def parse_outTransLatHist(key:str, val: str, r: dict):
    # Parse out transactions Histograms
    # Profiles an event that initiates a transaction in a peer controller
    # (e.g. an event that sends a request message)
    # Scalar RNF
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.outTransLatHist.(\w+)::(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        metric = m.group(4)
        cols = [
            f"cpu{cpuId}_{ncache}_CHI_outTransLatHist_{event}_{metric}",
            f"caches_{ncache}_CHI_outTransLatHist_{event}_{metric}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    # Histogram RNF
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.outTransLatHist\.(\w+)$"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        hist = {f"cpu{cpuId}_{ncache}_CHI_outTransLatHist_{event}_b{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    # Scalar HNF
    p = r"system\.ruby\.hnf(\d+)\.cntrl\.outTransLatHist\.(\w+)::(\w+)"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))
        event = m.group(2)
        metric = m.group(3)
        cols = [
            f"HNF{hnfId}_CHI_outTransLatHist_{event}_{metric}",
            f"HNF_CHI_outTransLatHist_{event}_{metric}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    # Histogram HNF
    p = r"system\.ruby\.hnf(\d+)\.cntrl\.outTransLatHist\.(\w+)$"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))
        event = m.group(2)
        hist = {f"HNF{hnfId}_CHI_outTransLatHist_{event}_b{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    return r


def parse_inTransLatHist(key:str, val: str, r: dict):
    # Parse in transactions Histograms
    # Profiles an event that initiates a protocol transactions for a specific
    # line (e.g. events triggered by incoming request messages).
    # A histogram with the latency of the transactions is generated for
    # all combinations of trigger event, initial state, and final state.

    # Scalar RNF
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.inTransLatHist\.(\w+)\.(\w+)\.(\w+)::(\w+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        inits = m.group(4)
        final = m.group(5)
        metric = m.group(6)

        cols = [
            f"cpu{cpuId}_{ncache}_CHI_inTransLatHist_{event}_{inits}_{final}_{metric}",
            f"caches_{ncache}_CHI_inTransLatHist_{event}_{inits}_{final}_{metric}",
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    # Histogram RNF
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.inTransLatHist\.(\w+)\.(\w+)\.(\w+)$"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        inits = m.group(4)
        final = m.group(5)
        hist = {f"cpu{cpuId}_{ncache}_CHI_inTransLatHist_{event}_{inits}_{final}_b{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    # Scalar HNF
    p = r"system\.ruby\.hnf(\d+)\.cntrl\.inTransLatHist\.(\w+)\.(\w+)\.(\w+)::(\w+)"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))

        event = m.group(2)
        inits = m.group(3)
        final = m.group(4)
        metric = m.group(5)

        cols = [
            f"HNF{hnfId}_CHI_inTransLatHist_{event}_{inits}_{final}_{metric}",
            f"HNF_CHI_inTransLatHist_{event}_{inits}_{final}_{metric}",
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    # Histogram HNF
    p = r"system\.ruby\.hnf(\d+)\.cntrl\.inTransLatHist\.(\w+)\.(\w+)\.(\w+)$"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))
        event = m.group(2)
        inits = m.group(3)
        final = m.group(4)
        hist = {f"HNF{hnfId}_CHI_inTransLatHist_{event}_{inits}_{final}_b{k}": int(v) for k,v in util.parse_gem5_histogram(val)}
        r.update(hist)
        return r

    # Total transactions ended RNF
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.\.inTransLatHist\.(\w+).(total|retries)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        metric = m.group(4)
        cols = [
            f"cpu{cpuId}_{ncache}_CHI_inTransLatHist_{event}_{metric}",
            f"caches_{ncache}_CHI_inTransLatHist_{event}_{metric}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    # Total transactions ended HNF
    p = r"system\.ruby\.hnf(\d+)\.cntrl\.\.inTransLatHist\.(\w+).(total|retries)"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))
        event = m.group(2)
        metric = m.group(3)

        cols = [
            f"HNF{hnfId}_CHI_inTransLatHist_{event}_{metric}",
            f"HNF_CHI_inTransLatHist_{event}_{metric}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r


    return r


def parse_outTransLatSpHist(key:str, val: str, r: dict):
    
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.outTransLatSpHist.(\w+)::(\d+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        bucket = m.group(4)
        #print(f"cpu{cpuId}_{ncache}_CHI_outTransLatSpHist_{event}")
        cols = [
            f"cpu{cpuId}_{ncache}_CHI_outTransLatSpHist_{event}_b{bucket}",
            f"caches_{ncache}_CHI_outTransLatSpHist_{event}_b{bucket}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    p = r"system\.ruby\.hnf(\d+)\.cntrl\.outTransLatSpHist.(\w+)::(\d+)"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))
        event = m.group(2)
        bucket = m.group(3)
        cols = [
            f"HNF{hnfId}_CHI_outTransLatSpHist_{event}_b{bucket}",
            f"HNF_CHI_outTransLatSpHist_{event}_b{bucket}"
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    return r


def parse_inTransLatSpHist(key:str, val: str, r: dict):

    # Scalar RNF
    p = r"system\.cpu(\d+)\.(l1d|l1i|l2)\.inTransLatSpHist\.(\w+)\.(\w+)\.(\w+)::(\d+)"
    m = re.match(p, key)
    if m:
        cpuId = int(m.group(1))
        ncache = m.group(2)
        event = m.group(3)
        inits = m.group(4)
        final = m.group(5)
        bucket = m.group(6)

        cols = [
            f"cpu{cpuId}_{ncache}_CHI_inTransLatSpHist_{event}_{inits}_{final}_b{bucket}",
            f"caches_{ncache}_CHI_inTransLatSpHist_{event}_{inits}_{final}_b{bucket}",
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    # Scalar HNF
    p = r"system\.ruby\.hnf(\d+)\.cntrl\.inTransLatSpHist\.(\w+)\.(\w+)\.(\w+)::(\d+)"
    m = re.match(p, key)
    if m:
        hnfId = int(m.group(1))
        event = m.group(2)
        inits = m.group(3)
        final = m.group(4)
        bucket = m.group(5)

        cols = [
            f"HNF{hnfId}_CHI_inTransLatSpHist_{event}_{inits}_{final}_b{bucket}",
            f"HNF_CHI_inTransLatSpHist_{event}_{inits}_{final}_b{bucket}",
        ]
        for c in cols:
            r = util.accumulate_num_col(c, val, r)
        return r

    return r


def parse_ruby_protocol(key:str, val: str, r: dict):

    r = parse_outTransLatHist(key, val, r)
    r = parse_inTransLatHist(key, val, r)

    r = parse_outTransLatSpHist(key, val, r)
    r = parse_inTransLatSpHist(key, val, r)

    return r
