from g5dbc.config import Config
from g5dbc.config.cpus import CoreFUDesc
from g5dbc.sim.m5_objects import attr_type_check
from g5dbc.sim.m5_objects.cpu import (
    m5_ArmO3CPU,
    m5_FUDesc,
    m5_FUPool,
    m5_OpClass,
    m5_OpDesc,
)

from ..AbstractCore import AbstractCore


class AbstractFUPool(m5_FUPool):
    def __init__(self, FU: dict[str, CoreFUDesc]):
        FUList: list[m5_FUDesc] = []
        for label, fu in FU.items():
            # Test for supported operations
            if m5_OpClass.is_supported([op.name for op in fu.ops]):
                _attr: dict = dict(
                    count=fu.count,
                    opList=[
                        m5_OpDesc(
                            opClass=op.name,
                            opLat=op.latency,
                            pipelined=op.pipelined,
                        )
                        for op in fu.ops
                    ],
                )
                # Test for label attribute
                if hasattr(m5_FUDesc, "label"):
                    _attr["label"] = label
                _cls = type(
                    label,
                    (m5_FUDesc,),
                    _attr,
                )
                FUList.append(_cls())
        super().__init__(FUList=FUList)


class Arm(m5_ArmO3CPU, AbstractCore):

    def __init__(self, config: Config, cpu_name: str, core_id: int, bp=None):
        cpu_conf = config.cpus[cpu_name]
        if cpu_conf.core is None:
            raise ValueError("Core config unavailable")
        _attr = {
            k: attr_type_check(m5_ArmO3CPU, k, v)
            for k, v in cpu_conf.core.to_dict().items()
            if hasattr(m5_ArmO3CPU, k)
        }
        for k, v in cpu_conf.extra_parameters.items():
            if hasattr(m5_ArmO3CPU, k):
                _attr[k] = v
        super().__init__(cpu_id=core_id, **_attr)
        self.fuPool = AbstractFUPool(cpu_conf.FU)
        if bp is not None:
            self.branchPred = bp

        self._core_id = core_id
        self._fs = config.simulation.full_system
        self._sve_vl = int(config.system.sve_vl) // 128

    def get_core_id(self) -> int:
        return self._core_id

    def get_mem_mode(self) -> str:
        return self.memory_mode()

    def create_threads(self) -> None:
        self.createThreads()
        self.set_isa_attr("sve_vl_se", self._sve_vl)

    def connect_interrupt(self) -> None:
        self.createInterruptController()

    def connect_icache(self, port) -> None:
        self.icache_port = port  # sequencer.in_ports

    def connect_dcache(self, port) -> None:
        self.dcache_port = port  # sequencer.in_ports

    def connect_walker_ports(self, port1, port2) -> None:
        self.mmu.dtb_walker.port = port1
        self.mmu.itb_walker.port = port2

    def set_isa_attr(self, attr, val) -> None:
        for j in range(self.numThreads):
            setattr(self.isa[j], attr, val)
            setattr(self.isa[j], attr, val)
