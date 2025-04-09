from g5dbc.config.cpus import BPredConf
from g5dbc.sim.m5_objects.cpu.bpred import m5_BiModeBP, m5_SimpleBTB, m5_TournamentBP


class BPredFactory:
    @staticmethod
    def create(conf: BPredConf | None):
        if conf is None:
            return None
        bpred = None
        match conf.model:
            case "BiMode":
                bpred = m5_BiModeBP(
                    btb=m5_SimpleBTB(**conf.BTB.to_dict()),
                    **{
                        k: v
                        for k, v in conf.settings.items()
                        if hasattr(m5_BiModeBP, k)
                    },
                )
            case "Tournament":
                bpred = m5_TournamentBP(
                    btb=m5_SimpleBTB(**conf.BTB.to_dict()),
                    **{
                        k: v
                        for k, v in conf.settings.items()
                        if hasattr(m5_TournamentBP, k)
                    },
                )
            case _:
                raise ValueError(f"BP model {conf.model} not available")

        return bpred
