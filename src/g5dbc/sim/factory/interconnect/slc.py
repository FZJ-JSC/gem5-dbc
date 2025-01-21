import math
from typing import Callable

from g5dbc.config import Config


# Generates SLC select bit masks as described
# in the Arm CMN-600 Technical Reference Manual
def slc_mask(cache_line_size=64, max_bits=52) -> Callable[[int], list[int]]:
    bs_bits = int(math.log2(cache_line_size))

    def mask(n: int):
        intlvBits = int(math.log2(n))
        mask_list = []
        for b in range(intlvBits):
            masks = [(1 << i) for i in range(b + bs_bits, max_bits, intlvBits)]
            m_i = 0
            for m_j in masks:
                m_i = m_i | m_j
            mask_list.append(m_i)
        return mask_list

    return mask


class MaskFactory:
    @staticmethod
    def create(config: Config) -> Callable[[int], list[int]]:

        cache_line_size = config.system.cache_line_size

        mask = slc_mask(cache_line_size=cache_line_size)

        return mask
