from g5dbc.config import Config
from g5dbc.sim.model.memory.AbstractMemSystem import AbstractMemSystem
from g5dbc.sim.model.memory.MultiChannelMem import MultiChannelMem

from .ctrl import MemCtrlFactory
class MemSystemFactory:
    @staticmethod
    def create(config: Config) -> AbstractMemSystem:
        mem_ctrls: list[MultiChannelMem] = []
        
        for numa_id, region in enumerate(config.memory.regions):            
            mem_ctrls.append(MultiChannelMem(region, MemCtrlFactory.create(region)))
        
        return AbstractMemSystem(mem_ctrls)
