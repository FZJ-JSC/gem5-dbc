from g5dbc.config import Config
from g5dbc.sim.m5_objects import m5_SrcClockDomain, m5_VoltageDomain
from g5dbc.sim.m5_objects.sim import m5_SubSystem

from .AbstractCore import AbstractCore


class AbstractProcessor(m5_SubSystem):
    """
    Abstract Processor
    """

    def __init__(
        self,
        config: Config,
        core_keys: list[str],
        core_group: dict[str, list[AbstractCore]],
    ) -> None:
        super().__init__()

        self._config = config
        self._core_group = core_group
        self._group_keys = [k for k in core_keys]
        self._active_idx = 0

        active_key = self._group_keys[self._active_idx]

        self._num_cpus = len(self._core_group[active_key])

        self.voltage_domain = m5_VoltageDomain()
        self.clk_domain = m5_SrcClockDomain(
            clock=config.system.clock, voltage_domain=self.voltage_domain
        )

        for key, cores in self._core_group.items():
            setattr(self, key, cores)
            for core in cores:
                core.create_threads()
                core.set_clock_domain(self.clk_domain)
                core.set_active(key == active_key)

    def get_clock_domain(self):
        return self.clk_domain

    def get_num_cpus(self) -> int:
        return self._num_cpus

    def get_active_core(self, core_id: int) -> AbstractCore:
        active_key = self._group_keys[self._active_idx]

        core_group = self._core_group[active_key]

        return core_group[core_id]

    def get_active_mem_mode(self) -> str:
        active_key = self._group_keys[self._active_idx]
        core_group = self._core_group[active_key]
        return core_group[0].get_mem_mode()

    def set_workload(self, process):
        for key, cores in self._core_group.items():
            for core in cores:
                core.set_workload(process)

    def switch_next(self) -> list[tuple[AbstractCore, AbstractCore]]:
        curr_key = self._group_keys[self._active_idx]
        next_key = self._group_keys[self._active_idx + 1]

        curr_cores = [core for core in self._core_group[curr_key]]
        next_cores = [core for core in self._core_group[next_key]]

        switch_cpus = list(zip(curr_cores, next_cores))

        self._active_idx += 1

        return switch_cpus
