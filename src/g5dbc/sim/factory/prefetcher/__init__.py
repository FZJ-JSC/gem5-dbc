from g5dbc.config.prefetcher import PrefetcherConf
from g5dbc.sim.m5_objects.prefetcher import (
    m5_AMPMPrefetcher,
    m5_BOPPrefetcher,
    m5_DCPTPrefetcher,
    m5_IndirectMemoryPrefetcher,
    m5_IrregularStreamBufferPrefetcher,
    m5_PIFPrefetcher,
    m5_SBOOEPrefetcher,
    m5_SignaturePathPrefetcher,
    m5_SignaturePathPrefetcherV2,
    m5_SlimAMPMPrefetcher,
    m5_SmsPrefetcher,
    m5_STeMSPrefetcher,
    m5_StridePrefetcher,
    m5_TaggedPrefetcher,
)


class PrefetcherFactory:
    @staticmethod
    def create(conf: PrefetcherConf):
        pf = None
        match conf.model:
            case "Tagged":
                pf = m5_TaggedPrefetcher(**conf.settings)
            case "Stride":
                pf = m5_StridePrefetcher(**conf.settings)
            case "IndirectMemory":
                pf = m5_IndirectMemoryPrefetcher(**conf.settings)
            case "SignaturePath":
                pf = m5_SignaturePathPrefetcher(**conf.settings)
            case "SignaturePathV2":
                pf = m5_SignaturePathPrefetcherV2(**conf.settings)
            case "AMPMP":
                pf = m5_AMPMPrefetcher(**conf.settings)
            case "DCPTP":
                pf = m5_DCPTPrefetcher(**conf.settings)
            case "IrregularStreamBuffer":
                pf = m5_IrregularStreamBufferPrefetcher(**conf.settings)
            case "SlimAMPM":
                pf = m5_SlimAMPMPrefetcher(**conf.settings)
            case "BOP":
                pf = m5_BOPPrefetcher(**conf.settings)
            case "Sms":
                pf = m5_SmsPrefetcher(**conf.settings)
            case "SBOOE":
                pf = m5_SBOOEPrefetcher(**conf.settings)
            case "STeMS":
                pf = m5_STeMSPrefetcher(**conf.settings)
            case "PIF":
                pf = m5_PIFPrefetcher(**conf.settings)
            case _:
                raise ValueError(f"Prefetcher model {conf.model} not available")

        return pf
