from pathlib import Path

from jsonschema import validate

from g5dbc.util import dict_json, dict_yaml


def test_default_configurations():
    """
    Validate configuration schema for example configurations
    """
    schema_file = (
        Path(__file__)
        .parents[1]
        .joinpath(
            "share",
            "gem5-dbc",
            "schema.json",
        )
    )

    config_files = (
        Path(__file__)
        .parents[1]
        .joinpath(
            "share",
            "gem5-dbc",
            "configs",
        )
        .glob("*/index.yaml")
    )

    for config_file in config_files:
        validate(
            instance=dict_yaml.read(config_file),
            schema=dict_json.read(schema_file),
        )
