import math

def add_row_id_col(data: list[dict]) -> list[dict]:
    """
    Sort parameter list and add row_id column
    """
    # sort dictionaries
    cols = [str(k) for k in data[0].keys()]
    rows = sorted([tuple(p[col] for col in cols) for p in data ])
    npad = math.ceil(math.log10(len(rows)))
    cols.append("row_id")
    idx_data = [dict( list(zip(cols,row)) ) for row in [ (*r, str(r_id).zfill(npad)) for r_id,r in enumerate(rows)]]

    return idx_data
