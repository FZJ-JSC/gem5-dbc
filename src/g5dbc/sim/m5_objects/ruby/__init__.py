import m5

from .sequencer import m5_RubySequencer


class m5_RubySystem(m5.objects.RubySystem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_network(self, network) -> None:
        self.network = network

    def set_num_of_sequencers(self, n: int) -> None:
        self.num_of_sequencers = n


class m5_RubyCache(m5.objects.RubyCache):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_RubyPortProxy(m5.objects.RubyPortProxy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
