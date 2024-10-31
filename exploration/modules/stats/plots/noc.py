import numpy as np

def resize_8CPUs_4x4_NOC(data):
    nrows, ncols = np.shape(data)
    data = np.insert(data, (0,3,6,6,8,8,8,8), 0, axis=1)
    data = np.reshape(data, (nrows, 4, 4))
    
    return data

def resize_16CPUs_4x4_NOC(data):
    res = list()
    for row in data:
        a = np.zeros((8,8))
        a[7][2] = row[0]
        a[7][4] = row[2]
        a[7][6] = row[4]

        a[6][3] = row[1]
        a[6][5] = row[3]
        a[6][7] = row[5]

        a[5][2] = row[6]
        a[5][4] = row[8]
        a[5][6] = row[10]

        a[4][3] = row[7]
        a[4][5] = row[9]
        a[4][7] = row[11]

        a[3][4] = row[12]
        a[3][6] = row[14]

        a[2][5] = row[13]
        a[2][7] = row[15]

        res.append(a)
    return res

def label_16CPUs_4x4_NOC(node: str):
    label = np.full((8,8), None)
    label[7][2] = f"{node}00"
    label[7][4] = f"{node}02"
    label[7][6] = f"{node}04"

    label[6][3] = f"{node}01"
    label[6][5] = f"{node}03"
    label[6][7] = f"{node}05"

    label[5][2] = f"{node}06"
    label[5][4] = f"{node}08"
    label[5][6] = f"{node}10"

    label[4][3] = f"{node}07"
    label[4][5] = f"{node}09"
    label[4][7] = f"{node}11"

    label[3][4] = f"{node}12"
    label[3][6] = f"{node}14"

    label[2][5] = f"{node}13"
    label[2][7] = f"{node}15"
    return label

def label_8CPUs_4x4_NOC(node: str):
    label = np.full((8,8), None)
    return label


def resize_to_noc(data, num_nodes, noc_rows=4, noc_cols=4):
    res = None
    if(num_nodes==8 and noc_rows==4 and noc_cols==4):
        res = resize_8CPUs_4x4_NOC(data)
    if(num_nodes==16 and noc_rows==4 and noc_cols==4):
        res = resize_16CPUs_4x4_NOC(data)
    
    return res

def noc_tile_labels(data, num_nodes, noc_rows=4, noc_cols=4, node: str = "CPU"):
    label = np.full((noc_rows,noc_rows), None)
    
    if(node == "CPU" and num_nodes==8 and noc_rows==4 and noc_cols==4):
        label = label_8CPUs_4x4_NOC(node)
    if(node == "CPU" and num_nodes==16 and noc_rows==4 and noc_cols==4):
        label = label_16CPUs_4x4_NOC(node)
    if(node == "SLC" and num_nodes==16 and noc_rows==4 and noc_cols==4):
        label = label_16CPUs_4x4_NOC(node)

    return label
