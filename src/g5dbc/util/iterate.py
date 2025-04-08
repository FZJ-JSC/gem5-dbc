import itertools


def iterate(m: dict) -> list[dict]:
    """Cartesian product over dictionary values

    Args:
        m (dict): Input dictionary

    Returns:
        list[dict]: List of all elements from the cartesian product over dictionary values
    """
    for k, v in m.items():
        if isinstance(v, list):
            pass
        else:
            m[k] = [v]
    k, v = zip(*m.items())
    l = list(dict(zip(k, p)) for p in itertools.product(*v))
    return l
