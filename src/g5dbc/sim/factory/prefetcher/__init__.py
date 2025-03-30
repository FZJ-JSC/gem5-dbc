from g5dbc.config.caches import PrefetcherConf
from g5dbc.sim.m5_objects.prefetcher import m5_StridePrefetcher, m5_TaggedPrefetcher


class PrefetcherFactory:
    @staticmethod
    def create(conf: PrefetcherConf):
        pf = None
        match conf.model:
            case "Tagged":
                pf = m5_TaggedPrefetcher(**conf.settings)
            case "Stride":
                pf = m5_StridePrefetcher(**conf.settings)
            case _:
                raise ValueError(f"Prefetcher model {conf.model} not available")

        return pf
