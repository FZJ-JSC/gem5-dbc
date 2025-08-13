from dataclasses import dataclass


@dataclass
class Options:
    resource_add: str
    resource_del: str
    resource_type: str
    resource_name: str
    resource_meta: str
    resource_arch: str
    resource_hash: str
    resource_version: str
    generate: str
    init_config: str
    parse: str
    evaluate: str
    validate: bool
    artifact_index: list[str]
    output_dir: str
    modules_dir: str
    configs_dir: str
    parser_regex_dir: str
    templates_dir: str
    workld_dir: str
    parsed_dir: str
    parser_format: str
    nprocs: int
    se_exec: str
    command: str = ""
