import itertools

def iterate(m: dict):
    for k,v in m.items():
        if isinstance(v, list):
            pass
        else:
            m[k] = [v]
    k, v = zip(*m.items())
    l = list(dict(zip(k, p)) for p in itertools.product(*v))
    return l
