
from modules.caches.caches import IOCache
from modules.caches.caches import L1I, L1D, WalkCache, L2, L3Slice

from modules.caches.prefetcher import Stride
from modules.caches.prefetcher import Tagged
from modules.caches.prefetcher import IndirectMemory
from modules.caches.prefetcher import SignaturePath
from modules.caches.prefetcher import SignaturePath2
from modules.caches.prefetcher import AMPM
from modules.caches.prefetcher import DCPT
from modules.caches.prefetcher import IrregularStreamBuffer
from modules.caches.prefetcher import SlimAMPM
from modules.caches.prefetcher import BOP
from modules.caches.prefetcher import SBOOE
from modules.caches.prefetcher import STeMS
from modules.caches.prefetcher import PIF


def get_prefetcher(options):
    def get_prefetcher_class(name: str):
        return dict(
            Stride=Stride,
            Tagged=Tagged,
            IndirectMemory=IndirectMemory,
            SignaturePath=SignaturePath,
            SignaturePath2=SignaturePath2,
            AMPM=AMPM,
            DCPT=DCPT,
            IrregularStreamBuffer=IrregularStreamBuffer,
            SlimAMPM=SlimAMPM,
            BOP=BOP,
            SBOOE=SBOOE,
            STeMS=STeMS,
            PIF=PIF
        ).get(name, None)
    pf_cls = get_prefetcher_class(options.selected)
    return pf_cls(parameters=options.configuration)
