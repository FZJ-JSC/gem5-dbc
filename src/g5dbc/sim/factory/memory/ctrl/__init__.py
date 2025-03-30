from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects.mem import m5_DRAMInterface
from g5dbc.sim.model.memory.AbstractMemCtrl import AbstractMemCtrl
from g5dbc.sim.model.memory.ctrl.DRAM_Ctrl import DRAM_Ctrl
from g5dbc.sim.model.memory.ctrl.Simple import SimpleMainMemory


class MemCtrlFactory:
    @staticmethod
    def create(config: MemoryRegionConfig) -> list[AbstractMemCtrl]:
        if config.isDRAM():
            _attr = dict(**config.dram_settings)
            for k, v in config.extra_parameters.items():
                if hasattr(m5_DRAMInterface, k):
                    _attr[k] = v

            _dram_cls = type(
                f"DRAM_{config.numa_id}",
                (m5_DRAMInterface,),
                _attr,
            )

            mem_ctrls = [
                DRAM_Ctrl(config, ctrl_id) for ctrl_id in range(config.channels)
            ]
            for ctrl in mem_ctrls:
                ctrl.set_dram_interface(dram=_dram_cls())
        else:
            mem_ctrls = [
                SimpleMainMemory(config, ctrl_id) for ctrl_id in range(config.channels)
            ]

        return mem_ctrls
