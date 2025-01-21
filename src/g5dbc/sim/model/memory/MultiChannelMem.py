from __future__ import annotations

import math

from g5dbc.config.memory import MemoryRegionConfig
from g5dbc.sim.m5_objects import m5_AddrRange

from .AbstractMemCtrl import AbstractMemCtrl


class MultiChannelMem:
    """
    Abstract Multi-Channel Memory
    """

    def __init__(
        self, config: MemoryRegionConfig, mem_ctrls: list[AbstractMemCtrl]
    ) -> None:
        """
        Initialize Multi-Channel Memory
        """
        self._config = config
        self._ctrls = mem_ctrls
        self._num_channels = config.channels
        self._xor_low_bit = config.xor_low_bit
        self._intlv_low_bit = int(math.log(config.intlv_size, 2))

    def set_memory_range(self, range: m5_AddrRange) -> None:
        """
        Set memory range among all controllers
        """

        intlv_bits = int(math.log(self._num_channels, 2))
        xor_high_bit = (
            self._xor_low_bit + intlv_bits - 1 if self._xor_low_bit > 0 else 0
        )

        for idx, ctrl in enumerate(self._ctrls):
            ctrl.set_addr_range(
                m5_AddrRange(
                    start=range.start,
                    size=range.size(),
                    intlvHighBit=self._intlv_low_bit + intlv_bits - 1,
                    xorHighBit=xor_high_bit,
                    intlvBits=intlv_bits,
                    intlvMatch=idx,
                )
            )

    def get_ctrl(self, ctrl_id: int) -> AbstractMemCtrl:
        return self._ctrls[ctrl_id]

    def controllers(self) -> list[AbstractMemCtrl]:
        return self._ctrls
