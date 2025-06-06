from g5dbc.config import Config
from g5dbc.sim.m5_objects.sim import m5_Root
from g5dbc.sim.m5_objects.util import (
    m5_curTick,
    m5_disableAllListeners,
    m5_instantiate,
    m5_MaxTick,
    m5_simulate,
    m5_switchCpus,
)
from g5dbc.sim.model.board import AbstractBoardSystem


class SimulationDriver:

    def __init__(self, config: Config, system: AbstractBoardSystem) -> None:
        self.system = system
        self.config = config

        system.generate_dtb()

        self.max_tick = m5_MaxTick()

        if config.simulation.disable_listeners:
            print("Disabling Listeners")
            m5_disableAllListeners()

        self.root = m5_Root(system=system, full_system=config.simulation.full_system)

    def run(self):
        m5_instantiate()

        # simulate
        print("m5.simulate")
        exit_event = m5_simulate(self.max_tick - m5_curTick())
        exit_cause = exit_event.getCause()

        # switch cpus
        print("m5.switchCpus")
        m5_switchCpus(self.system, self.system.switch_cpus())

        # simulate
        print("m5.simulate")
        exit_event = m5_simulate(self.max_tick - m5_curTick())
        exit_cause = exit_event.getCause()

        print(f"{exit_event.getCause()} {exit_event.getCode()}")
