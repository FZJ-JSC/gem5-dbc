from g5dbc.config import Config
from g5dbc.sim.m5_objects.dev import m5_Terminal, m5_VncServer
from g5dbc.sim.model.board.AbstractBoardSystem import AbstractBoardSystem
from g5dbc.sim.model.board.arm.ArmBoardSystem import ArmBoardSystem
from g5dbc.sim.model.board.arm.platform import ArmVExpressV1, ArmVExpressV2


class BoardFactory:
    @staticmethod
    def create(config: Config) -> AbstractBoardSystem:
        match config.system.platform:
            case "VExpress_GEM5_V1":
                realview = ArmVExpressV1()
            case "VExpress_GEM5_V2":
                realview = ArmVExpressV2()
            case _:
                raise ValueError(f"Platform model {config.system.platform} not available")

        board = ArmBoardSystem(
            config=config,
            highest_el_is_64 = True,
            sve_vl = int(config.system.sve_vl) / 128,
            cache_line_size=config.system.cache_line_size,
            terminal  = m5_Terminal(),
            vncserver = m5_VncServer(),
            realview  = realview
        )

        return board
