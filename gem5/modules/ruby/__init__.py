
import m5

import importlib

from modules.ruby.memory import configure_mem_region_controller


def configure_ruby(system, options, piobus = None, dma_ports = [], bootmem=None):
    protocol_name = m5.defines.buildEnv['PROTOCOL']

    protocol = importlib.import_module(f"modules.ruby.protocol.{protocol_name}")

    protocol.configure_ruby(system, options, piobus, dma_ports, bootmem)