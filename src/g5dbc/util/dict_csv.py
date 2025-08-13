import csv
from pathlib import Path


def read(file: Path) -> list[dict]:
    """Read CSV file and return a list of rows

    Args:
        file (Path): CSV file path

    Returns:
        list[dict]: List of rows
    """
    data = []
    if file.is_file():
        with file.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                data.append(row)
    return data


def write(file: Path, data: list[dict]) -> list[dict]:
    """Write a list of rows to a CSV file.
       If list is empty, no file is written.

    Args:
        file (Path): CSV file path
        data (list[dict]): Data to write to file, as a list of rows

    Returns:
        list[dict]: Data written to file
    """
    if not data:
        return data

    fields = set()
    for r in data:
        fields.update(r.keys())

    with file.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=sorted([f for f in fields]),
            dialect="unix",
            restval=float("nan"),
        )
        writer.writeheader()
        writer.writerows(data)

    return data
