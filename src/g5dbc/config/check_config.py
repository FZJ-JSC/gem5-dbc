import math

from .config import Config


def check_config(config: Config) -> bool:
    """
    Check Parameter constraints
    """

    assert (
        config.interconnect.garnet.data_width == config.interconnect.simple.data_width
    ), "Data width inconsistency"
    config.network.data_width = config.interconnect.garnet.data_width

    config.memory.controller.data_channel_size = config.network.data_width
    for name, conf in config.caches.items():
        if conf.controller is not None:
            conf.controller.data_channel_size = config.network.data_width
        conf.block_size_bits = int(math.log(config.system.cache_line_size, 2))

    return True
