import json

from jsonschema import validate
from jsonschema.validators import Draft202012Validator

from ..util import yaml_dict
from .config_file import read_config_file, write_config_file
from .options import Options


def validate_config(opts: Options) -> int:

    config_file = opts.validate

    print(f"validate {config_file}")
    config_dict = yaml_dict.load(config_file)

    schema_file = opts.user_data_dir.joinpath("schema.json")

    with schema_file.open("r", encoding="UTF-8") as stream:
        schema_dict = json.load(stream)

    validate(instance=config_dict, schema=schema_dict)
    # Read default benchmark configuration
    # config = read_config_file(config_path)
