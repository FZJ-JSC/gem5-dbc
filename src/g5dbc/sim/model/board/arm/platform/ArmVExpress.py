from g5dbc.sim.m5_objects.dev.platform import m5_VExpress_GEM5_V1, m5_VExpress_GEM5_V2
from g5dbc.sim.m5_objects.mem import m5_SimpleMemory


class ArmPlatform:
    """
    Abstract Arm Platform
    """

    def get_bootmem(self) -> m5_SimpleMemory:
        return self.bootmem

    def connect_global_interrupt(self, board) -> None:
        if hasattr(self.gic, "cpu_addr"):
            board.gic_cpu_addr = self.gic.cpu_addr


class ArmVExpressV1(m5_VExpress_GEM5_V1, ArmPlatform):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ArmVExpressV2(m5_VExpress_GEM5_V2, ArmPlatform):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
