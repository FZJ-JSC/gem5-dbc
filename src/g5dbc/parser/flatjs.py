from .parser import StatsParser


class FlatJS(StatsParser):

    def update_column(self, r: dict, c: str, key, val) -> dict:
        if key is None:
            try:
                r[c] = val + r.get(c, 0)
            except Exception as e:
                print(f"Warning: col={c} err={e}")
        elif key == "total" or key == "samples":
            c = f"{c}_total"
            r[c] = val + r.get(c, 0)
        elif key == "sum":
            c = f"{c}_sum"
            r[c] = val + r.get(c, 0)
        elif key == "values" or key == "list":
            for k, v in val:
                d = r.setdefault(c, dict())
                d[k] = v + d.get(k, 0)
        else:
            d = r.setdefault(c, dict())
            d[key] = val + d.get(key, 0)

        return r

    def update_terminal_output(self, r: dict, parsed_output: dict) -> dict:
        return r
