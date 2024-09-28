from g5dbc.config import Config
from g5dbc.sim.model.interconnect.CoherentInterconnect import CoherentInterconnect
from g5dbc.sim.model.interconnect.ruby.RubyInterconnect import RubyInterconnect


class InterconnectFactory:
    @staticmethod
    def create(config: Config) -> CoherentInterconnect:
        
        ic = RubyInterconnect(config)
        
        return ic
        