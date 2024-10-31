import pandas
from pathlib import Path


def read_rows(data_directory: Path, select_rows: dict, fmtstr: str = "{benchmark}_data_selected.h5"):
    if fmtstr.endswith("h5"):
        return read_rows_hdf5(data_directory, select_rows, fmtstr)
    if fmtstr.endswith("csv"):
        return read_rows_csv(data_directory, select_rows, fmtstr)
    if fmtstr.endswith("txt"):
        return read_rows_csv(data_directory, select_rows, fmtstr)
    return None

def read_rows_hdf5(data_directory: Path, select_rows: dict, fmtstr: str = "{benchmark}_data_selected.h5"):
    
    fn = data_directory.joinpath(fmtstr.format(**select_rows))
    df = pandas.read_hdf(fn)

    benchmark = select_rows['benchmark']
    slct = (df['benchmark']==benchmark)
    
    for key,val in select_rows.items():
        if key.startswith("not_"):
            slct=slct&(df[key.replace("not_","")]!=val)
        else:
            slct=slct&(df[key]==val)
    rows = df[slct]
    return rows

def read_rows_csv(data_directory: Path, select_rows: dict, fmtstr: str = "{benchmark}_cols.txt"):
    
    fn = data_directory.joinpath(fmtstr.format(**select_rows))
    df = pandas.read_csv(fn)

    benchmark = select_rows['benchmark']
    slct = (df['benchmark']==benchmark)
    
    for key,val in select_rows.items():
        if key.startswith("not_"):
            slct=slct&(df[key.replace("not_","")]!=val)
        else:
            slct=slct&(df[key]==val)
        
    rows = df[slct]
    return rows
