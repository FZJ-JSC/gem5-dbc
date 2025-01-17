from g5dbc.config import Config
from g5dbc.config.cpus import CoreFUDesc, CPUConf
from g5dbc.sim.m5_objects.cpu import m5_ArmO3CPU, m5_FUDesc, m5_FUPool, m5_OpDesc
from g5dbc.sim.m5_objects.ruby import Sequencer

from ..AbstractCore import AbstractCore


class AbstractFUPool(m5_FUPool):
    def __init__(self, FU: dict[str, CoreFUDesc]):
        FUList: list[m5_FUDesc] = []
        for name, fu in FU.items():
            _cls = type(
                name,
                (m5_FUDesc,),
                dict(
                    count=fu.count,
                    opList=[
                        m5_OpDesc(
                            opClass=op.name, opLat=op.latency, pipelined=op.pipelined
                        )
                        for op in fu.ops
                    ],
                ),
            )
            FUList.append(_cls())
        super().__init__(FUList=FUList)


class ArmCore(m5_ArmO3CPU, AbstractCore):

    def __init__(self, cpu_conf: CPUConf, core_id: int = 0):
        if cpu_conf.core is None:
            raise ValueError("Core config unavailable")

        super().__init__(cpu_id=core_id, **cpu_conf.core.to_dict())
        self.fuPool = AbstractFUPool(cpu_conf.FU)

    def set_branchPred(self, bp) -> None:
        self.branchPred = bp

    def create_threads(self) -> None:
        self.createThreads()

    def connect_interrupt(self) -> None:
        self.createInterruptController()

    def connect_icache(self, sequencer: Sequencer) -> None:
        self.icache_port = sequencer.in_ports

    def connect_dcache(self, sequencer: Sequencer) -> None:
        self.dcache_port = sequencer.in_ports

    def connect_walker_ports(self, port1, port2) -> None:
        self.mmu.dtb_walker.port = port1.in_ports
        self.mmu.itb_walker.port = port2.in_ports
