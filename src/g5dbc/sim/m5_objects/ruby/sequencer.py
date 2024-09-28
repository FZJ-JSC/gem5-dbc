import m5

class Versions:
    _seqs = 0
    @classmethod
    def getSeqId(cls):
        val = cls._seqs
        cls._seqs += 1
        return val

class Sequencer(m5.objects.RubySequencer):
    def __init__(self, **kwargs):
        super().__init__(
            version     = Versions.getSeqId(),
            **kwargs
        )
    
    def connect_IO_bus(self, iobus) -> None:
        self.connectIOPorts(iobus)
    
    def set_clock_domain(self, clk_domain) -> None:
        self.clk_domain = clk_domain
    
    def get_version(self) -> int:
        return self.version.value
