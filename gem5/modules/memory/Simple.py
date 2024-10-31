
import m5

class Simple(m5.objects.SimpleMemory):
    def __init__(self, options, **kwargs):
        super(Simple, self).__init__(**kwargs)
        self.latency     = options.architecture.memory[0].simple_latency
        self.latency_var = options.architecture.memory[0].simple_latency_var
        self.bandwidth   = options.architecture.memory[0].simple_bandwidth
