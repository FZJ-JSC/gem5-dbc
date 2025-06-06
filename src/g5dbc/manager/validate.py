from pathlib import Path

from jsonschema import validate

from ..util import dict_json, dict_yaml
from .options import Options


def validate_config(opts: Options):
    """Validate configuration file

    Args:
        opts (Options): Command line options
    """

    config_path = Path(opts.init_config)

    schema_file = Path(opts.configs_dir).joinpath("schema.json")

    print(f"Validating {config_path} using schema {schema_file}")

    validate(
        instance=dict_yaml.read(config_path),
        schema=dict_json.read(schema_file),
    )
