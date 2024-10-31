
def concatenate_columns(rows, cols):

    if isinstance(cols, str):
        return (rows,cols)

    lbl_col = "_".join(cols)
    fmt_str = "}_{".join(cols).join(["{","}"])

    rows[lbl_col] = rows.apply(lambda row: fmt_str.format(**row), axis='columns')

    return (rows,lbl_col)

