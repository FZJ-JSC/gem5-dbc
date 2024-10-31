"""
Methods for row aggretation
"""

def aggregate_statistics(rows, agg_col: str, uniq_cols: list ):
    """
    Aggregate statistics
    """
    res = rows[uniq_cols+[agg_col]].groupby(uniq_cols)[agg_col].describe()
    res.reset_index(inplace=True)

    return (res, agg_col)

def aggregate_list(rows, agg_col: str, uniq_cols: list ):
    """
    Aggregate list
    """
    res = rows[uniq_cols+[agg_col]].groupby(uniq_cols)[agg_col].apply(list)
    res = res.reset_index(name=agg_col)

    return (res, agg_col)
