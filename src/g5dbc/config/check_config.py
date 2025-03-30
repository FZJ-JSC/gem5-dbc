import math

from .config import Config


def check_config(config: Config) -> bool:
    """
    Check configuration parameter constraints
    """

    if config.network.clock == "":
        config.network.clock = config.system.clock

    if config.interconnect.garnet is not None:
        config.interconnect.garnet.data_width = config.network.data_width
        config.interconnect.garnet.data_link_width = (
            config.interconnect.garnet.cntrl_msg_size
            + config.interconnect.garnet.data_width
        )
        config.interconnect.garnet.link_width_bits = (
            config.interconnect.garnet.data_link_width * 8
        )

    if config.interconnect.simple is not None:
        config.interconnect.simple.data_width = config.network.data_width

    config.memory.controller.data_channel_size = config.network.data_width
    for name, conf in config.caches.items():
        if conf.controller is not None:
            conf.controller.data_channel_size = config.network.data_width
        conf.block_size_bits = int(math.log(config.system.cache_line_size, 2))

    if config.system.architecture == "arm64":
        match config.interconnect.model:
            case "classic":
                config.system.platform = "VExpress_GEM5_V1"
            case "simple":
                config.system.platform = "VExpress_GEM5_V2"
            case "garnet":
                config.system.platform = "VExpress_GEM5_V2"

    return True
