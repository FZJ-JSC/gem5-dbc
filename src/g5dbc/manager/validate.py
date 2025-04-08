from pathlib import Path

from jsonschema import validate

from ..util import dict_json, dict_yaml
from .options import Options


def validate_config(opts: Options, path_cfg: Path):
    """Validate configuration file

    Args:
        opts (Options): Command line options
        path_cfg (Path): Configuration file to validate
    """

    schema_file = opts.user_data_dir.joinpath("schema.json")

    print(f"Validating {path_cfg}")

    validate(
        instance=dict_yaml.read(path_cfg),
        schema=dict_json.read(schema_file),
    )
