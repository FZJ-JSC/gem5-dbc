from ...util.parser import parse_number_str
from . import StatsParser


class FlatJS(StatsParser):

    def update_column(self, r: dict, c: str, key, val) -> dict:
        scalar_keys = [
            "total",
            "samples",
            "sum",
            "window",
            "average",
            "variance",
        ]
        map_keys = [
            "values",
            "list",
        ]
        vec_keys = [
            "correlator",
            "array",
            "averages",
            "variances",
            "counts",
            "bin_samples",
        ]
        list_keys = ["selected"]

        try:
            if key is None:
                r[c] = val + r.get(c, 0)
            elif key in scalar_keys:
                c = f"{c}_{key}"
                r[c] = val + r.get(c, 0)
            elif key in map_keys:
                c = f"{c}_{key}"
                if isinstance(val, list):
                    for k, v in val:
                        d = r.setdefault(c, dict())
                        d[k] = v + d.get(k, 0)
            elif key in vec_keys:
                c = f"{c}_{key}"
                l = val.split(",")
                n = len(l) - 1
                b = r.setdefault(c, [0] * n)
                n = min(n, len(b))
                for i in range(n):
                    b[i] = parse_number_str(l[i])
            elif key in list_keys:
                c = f"{c}_{key}"
                r[c] = val
            else:
                c = f"{c}_{key}"
                d = r.setdefault(c, dict())
                d[key] = val + d.get(key, 0)

        except Exception as e:
            print(f"Parser Error {e=} at {c=} {key=}")

        return r

    def update_terminal_output(self, r: dict, parsed_output: dict) -> dict:
        return r
