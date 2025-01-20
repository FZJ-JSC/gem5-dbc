from g5dbc.config.bpred import BPredConf
from g5dbc.sim.m5_objects.cpu.bpred import m5_BiModeBP, m5_SimpleBTB, m5_TournamentBP


class BPredFactory:
    @staticmethod
    def create(bp_conf: BPredConf):
        bp = None
        btb = m5_SimpleBTB(**bp_conf.BTB.to_dict())
        match bp_conf.model:
            case "BiMode":
                bp = m5_BiModeBP(btb=btb, **bp_conf.params)
            case "Tournament":
                bp = m5_TournamentBP(btb=btb, **bp_conf.params)
            case _:
                raise ValueError(f"BP model {bp_conf.model} not available")

        return bp
