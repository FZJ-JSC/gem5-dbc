from g5dbc.sim.m5_objects.ruby import m5_RubySequencer


class Sequencer(m5_RubySequencer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def connect_IO_bus(self, iobus) -> None:
        self.connectIOPorts(iobus)

    def set_clock_domain(self, clk_domain) -> None:
        self.clk_domain = clk_domain

    def get_version(self) -> int:
        return self.version.value
