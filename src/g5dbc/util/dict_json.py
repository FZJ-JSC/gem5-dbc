import json
from pathlib import Path


def read(file: Path) -> dict:
    """Read JSON file to Python dict

    Args:
        file (Path): JSON file path

    Returns:
        dict: JSON file contents as Python dict
    """

    with file.open("r", encoding="UTF-8") as stream:
        data = json.load(stream)

    return data


def write(file: Path, data: dict) -> dict:
    """Write Python dict to YAML file

    Args:
        file (Path): JSON file path
        data (dict): Python dict

    Returns:
        dict: Python dict
    """
    with file.open("w", encoding="UTF-8") as stream:
        json.dump(data, stream)
    return data
