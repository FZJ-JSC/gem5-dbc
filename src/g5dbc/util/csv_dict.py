import csv
from pathlib import Path

def write(file: Path, data: list[dict] ):    
    assert(len(data) > 0)
    with file.open('w', encoding='utf-8', newline='') as stream:
        fields = data[0].keys()
        writer = csv.DictWriter(stream, fieldnames=fields, dialect='unix',)
        writer.writeheader()
        writer.writerows(data)

    return data
